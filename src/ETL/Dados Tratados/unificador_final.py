import pandas as pd
import numpy as np
import os

input_folder = '.'
output_folder = 'Dados Unificados'
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, 'dataset_final_modelagem.csv')

print("Iniciando a Unificacao Mestra (Pipeline 2.1 - Tratamento de NaN refinado)...")

# 1. Carregar arquivos processados
df_censo = pd.read_csv(os.path.join(input_folder, 'censo_processado.csv'))
df_pib = pd.read_csv(os.path.join(input_folder, 'pib_processado.csv'))
df_frota = pd.read_csv(os.path.join(input_folder, 'renavam_fevereiro_processado.csv'))
df_snv = pd.read_csv(os.path.join(input_folder, 'infraestrutura_snv_processado.csv'))

# 2. Padronizacao de chaves
print("Padronizando tipos de dados das chaves...")

def limpar_codigo(col):
    return col.astype(str).str.replace('.0', '', regex=False).str.strip()

df_censo['codigo'] = limpar_codigo(df_censo['codigo'])
df_pib['codigo'] = limpar_codigo(df_pib['codigo'])

for df in [df_censo, df_pib, df_frota, df_snv]:
    if 'chave_merge' in df.columns:
        df['chave_merge'] = df['chave_merge'].astype(str).str.strip().str.upper()

# 3. Unificacao Sequencial
print("Cruzando Censo + PIB...")
colunas_pib = ['codigo', 'vab_agro', 'vab_industria', 'vab_servicos', 'pib_per_capita']
df_master = pd.merge(df_censo, df_pib[colunas_pib], on='codigo', how='left')

vazios_pib = df_master['vab_agro'].isna().sum()
if vazios_pib > 0:
    print(f"  Atencao: {vazios_pib} municipios sem dados de PIB apos merge")

print("Cruzando com dados da Frota (RENAVAM)...")
cols_frota = ['chave_merge', 'TOTAL', 'AUTOMOVEL', 'CAMINHONETE', 'MOTOCICLETA', 'UTILITARIO', 'DIESEL', 'FLEX']
df_master = pd.merge(df_master, df_frota[cols_frota], on='chave_merge', how='left')

vazios_frota = df_master['TOTAL'].isna().sum()
if vazios_frota > 0:
    print(f"  Atencao: {vazios_frota} municipios sem dados de frota apos merge")

print("Cruzando com dados de Infraestrutura (DNIT)...")
cols_dnit = ['chave_merge', 'extensao_total_km', 'km_pavimentado', 'km_terra', 'presenca_rodovia_federal']
df_master = pd.merge(df_master, df_snv[cols_dnit], on='chave_merge', how='left')

# 4. Conversao numerica explicita
cols_numericas = ['TOTAL', 'AUTOMOVEL', 'CAMINHONETE', 'MOTOCICLETA', 'UTILITARIO',
                  'DIESEL', 'FLEX', 'vab_agro', 'vab_industria', 'vab_servicos',
                  'pib_per_capita', 'populacao', 'area', 'extensao_total_km',
                  'km_pavimentado', 'km_terra']
for col in cols_numericas:
    if col in df_master.columns:
        df_master[col] = pd.to_numeric(df_master[col], errors='coerce')

# 5. Tratamento de NaN justificado por variavel (atende feedback do professor)
print("Aplicando tratamento de NaN justificado por variavel...")

# Variaveis de frota: NaN apos merge significa "municipio sem registro RENAVAM",
# o que neste contexto e equivalente a frota zero (categoria nao registrada)
for col in ['TOTAL', 'AUTOMOVEL', 'CAMINHONETE', 'MOTOCICLETA', 'UTILITARIO', 'DIESEL', 'FLEX']:
    df_master[col] = df_master[col].fillna(0)

# Infraestrutura: ausencia no DNIT = sem rodovia federal (binarizada)
df_master['presenca_rodovia_federal'] = df_master['presenca_rodovia_federal'].fillna(0).astype(int)
df_master['extensao_total_km'] = df_master['extensao_total_km'].fillna(0)
df_master['km_pavimentado'] = df_master['km_pavimentado'].fillna(0)
df_master['km_terra'] = df_master['km_terra'].fillna(0)

# PIB e Censo: NaN aqui e dado realmente ausente, NAO preenchemos com zero.
# Mantemos NaN e a etapa de modelagem deve excluir esses registros explicitamente.
n_pib_nan = df_master['vab_agro'].isna().sum()
n_pop_nan = df_master['populacao'].isna().sum()
print(f"  Mantidos como NaN (dados realmente ausentes):")
print(f"    PIB: {n_pib_nan} municipios")
print(f"    Populacao: {n_pop_nan} municipios")

# 6. Feature Engineering com tratamento correto de divisao por zero
print("Calculando indicadores derivados...")

# Proporcoes da frota: so calcula se TOTAL > 0, caso contrario e NaN
mask_frota_valida = df_master['TOTAL'] > 0
df_master['target_perc_utilitarios'] = np.where(
    mask_frota_valida,
    (df_master['UTILITARIO'] / df_master['TOTAL']) * 100,
    np.nan
)
df_master['target_perc_diesel'] = np.where(
    mask_frota_valida,
    (df_master['DIESEL'] / df_master['TOTAL']) * 100,
    np.nan
)

# Indicadores per capita: so calcula se populacao > 0, caso contrario e NaN
mask_pop_valida = df_master['populacao'] > 0
df_master['pib_agro_por_habitante'] = np.where(
    mask_pop_valida & df_master['vab_agro'].notna(),
    df_master['vab_agro'] / df_master['populacao'],
    np.nan
)
df_master['km_terra_por_habitante'] = np.where(
    mask_pop_valida,
    df_master['km_terra'] / df_master['populacao'],
    np.nan
)

# Resumo final
print("\nResumo de NaN no dataset final:")
print(df_master.isna().sum()[df_master.isna().sum() > 0].to_string())
print(f"\nShape final: {df_master.shape}")

# Salvar
df_master.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nCONCLUIDO. Arquivo: {output_file}")
