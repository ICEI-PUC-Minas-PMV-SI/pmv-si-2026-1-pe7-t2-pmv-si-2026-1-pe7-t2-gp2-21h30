import pandas as pd
import os
import unicodedata

# Definir o caminho da pasta de saída
output_path = 'Dados Tratados'

# Cria a pasta caso ela não exista
if not os.path.exists(output_path):
    os.makedirs(output_path)

# 1. Carregando as duas abas
file_path = '../Dados/Censo Demografico Area Territorial.xlsx'

# 2. Função de Limpeza de String (Para criar chaves de busca sem erros de acento)
def normalizar_nome(txt):
    if pd.isna(txt): return ""
    # Remove o que estiver dentro de parênteses (ex: " (RO)")
    txt = str(txt).split('(')[0].strip().upper()
    # Remove acentos e cedilhas
    nfkd_form = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Lendo População (Aba 1) - Pulando as 3 primeiras linhas de metadados
df_pop = pd.read_excel(file_path, sheet_name=0, skiprows=3)
df_pop.columns = ['codigo', 'municipio', 'populacao']

# Lendo Área (Aba 2) - Pulando as 3 primeiras linhas de metadados
df_area = pd.read_excel(file_path, sheet_name=1, skiprows=3)
df_area.columns = ['codigo', 'municipio', 'area']

# 2. Limpeza de dados
# Garantir que o código seja string e remover linhas de rodapé
df_pop = df_pop[df_pop['codigo'].notna()].copy()
df_area = df_area[df_area['codigo'].notna()].copy()

# Padronizar separador decimal em strings. Substituir vírgula por ponto e converter para float.
df_area['area'] = df_area['area'].astype(str).str.replace(',', '.').astype(float)
df_pop['populacao'] = pd.to_numeric(df_pop['populacao'], errors='coerce')

# 3. Merge das abas (Unindo População e Área pelo Código do Município)
df_censo = pd.merge(df_pop, df_area, on=['codigo', 'municipio'])

# CRIAÇÃO DAS CHAVES DE INTEGRAÇÃO
# Extraímos a UF do nome original (ex: de "Ariquemes (RO)" para "RO")
df_censo['uf'] = df_censo['municipio'].str.extract(r'\((.*?)\)')

# Criamos a chave normalizada (ex: "Alta Floresta D'Oeste (RO)" vira "ALTA FLORESTA D'OESTE_RO")
df_censo['municipio_limpo'] = df_censo['municipio'].apply(normalizar_nome)
df_censo['chave_merge'] = df_censo['municipio_limpo'] + "_" + df_censo['uf'].fillna('')

# 4. Cálculo da Densidade Demográfica (Habitantes por km²)
df_censo['densidade_demografica'] = df_censo['populacao'] / df_censo['area']

# 7. Exportação
# Dataset com a 'chave_merge'. Será usada para os dados do SENATRAN e do DNIT.
df_censo.to_csv(os.path.join(output_path, 'censo_processado.csv'), index=False, encoding='utf-8-sig')


# Visualização rápida e exportação
print(f"Censo processado! Total de municípios: {len(df_censo)}")
print("Amostra das chaves de integração criadas:")
print(df_censo[['codigo', 'municipio', 'chave_merge']].head())