import pandas as pd
import os

# CONFIGURAÇÃO DE CAMINHOS DINÂMICA
input_folder = '.' 
output_folder = 'Dados Unificados' 
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, 'dataset_final_modelagem.csv')

print("🚀 Iniciando a Unificação Mestra (Pipeline 2.0)...")

# 1. Carregar os arquivos
df_censo = pd.read_csv(os.path.join(input_folder, 'censo_processado.csv'))
df_pib = pd.read_csv(os.path.join(input_folder, 'pib_processado.csv'))
df_frota = pd.read_csv(os.path.join(input_folder, 'renavam_fevereiro_processado.csv'))
df_snv = pd.read_csv(os.path.join(input_folder, 'infraestrutura_snv_processado.csv'))

# --- SOLUÇÃO DO ERRO: FORÇAR TIPO STRING NAS CHAVES ---
print("🔧 Padronizando tipos de dados das chaves...")

# Função interna para limpar códigos IBGE (garante 7 dígitos em string)
def limpar_codigo(col):
    return col.astype(str).str.replace('.0', '', regex=False).str.strip()

df_censo['codigo'] = limpar_codigo(df_censo['codigo'])
df_pib['codigo'] = limpar_codigo(df_pib['codigo'])

# Garantir que as chaves de texto também estejam limpas e em string
for df in [df_censo, df_pib, df_frota, df_snv]:
    if 'chave_merge' in df.columns:
        df['chave_merge'] = df['chave_merge'].astype(str).str.strip().str.upper()

# 2. Unificação Sequencial
print("🔗 Cruzando Censo + PIB...")
colunas_pib = ['codigo', 'vab_agro', 'vab_industria', 'vab_servicos', 'pib_per_capita']

df_master = pd.merge(df_censo, df_pib[colunas_pib], on='codigo', how='left')

# DEBUG: Verificar se o PIB "entrou" no df_master
vazios_pib = df_master['vab_agro'].isna().sum()
if vazios_pib > 0:
    print(f"⚠️ Atenção: {vazios_pib} municípios ficaram sem dados de PIB após o merge!")

print("🔗 Cruzando com dados da Frota (RENAVAM)...")
# Note que aqui usamos a 'chave_merge' que já tratamos como string acima
cols_frota = ['chave_merge', 'TOTAL', 'AUTOMOVEL', 'CAMINHONETE', 'MOTOCICLETA', 'UTILITARIO', 'DIESEL', 'FLEX']
df_master = pd.merge(df_master, df_frota[cols_frota], on='chave_merge', how='left')

print("🔗 Cruzando com dados de Infraestrutura (DNIT)...")
cols_dnit = ['chave_merge', 'extensao_total_km', 'km_pavimentado', 'km_terra', 'presenca_rodovia_federal']

df_master = pd.merge(
    df_master, 
    df_snv[cols_dnit], 
    on='chave_merge', 
    how='left'
)

df_master['presenca_rodovia_federal'] = df_master['presenca_rodovia_federal'].fillna(0).astype(int)

# 3. Tratamento de Nulos e Conversão Numérica Final
# Converter para numérico
cols_calc = ['TOTAL', 'UTILITARIO', 'DIESEL', 'vab_agro', 'populacao', 'km_terra']
for col in cols_calc:
    if col in df_master.columns:
        df_master[col] = pd.to_numeric(df_master[col], errors='coerce')


# 4. Feature Engineering Final
print("📊 Calculando indicadores para o Machine Learning...")
pop = df_master['populacao'].replace(0, 1)
total_f = df_master['TOTAL'].replace(0, 1)

df_master['target_perc_utilitarios'] = (df_master['UTILITARIO'].fillna(0) / total_f) * 100
df_master['target_perc_diesel'] = (df_master['DIESEL'].fillna(0) / total_f) * 100
df_master['pib_agro_por_habitante'] = df_master['vab_agro'].fillna(0) / pop
df_master['km_terra_por_habitante'] = df_master['km_terra'].fillna(0) / pop

df_master = df_master.fillna(0)

# Salvamento Final
df_master.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✅ CONCLUÍDO! Verifique o arquivo em: {output_file}")