import pandas as pd
import os
import unicodedata

# 1. Função de Normalização Padronizada
def normalizar_nome(txt):
    if pd.isna(txt): return ""
    txt = str(txt).split('(')[0].strip().upper()
    nfkd_form = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Configuração de caminhos
input_folder = '../Dados'
output_folder = 'Dados Tratados'
os.makedirs(output_folder, exist_ok=True)

def processar_renavam():
    print("Iniciando ETL do RENAVAM - Fevereiro 2026...")

    # 1. TIPO (Usamos a engine='openpyxl' para otimização)
    print("Lendo arquivo de TIPO...")
    df_tipo = pd.read_excel(os.path.join(input_folder, 'frotapormunicipioetipofevereiro2026.xlsx'), skiprows=2)
    # Limpar linhas de cabeçalho repetidas e totais
    df_tipo = df_tipo[df_tipo['UF'] != 'UF'].dropna(subset=['MUNICIPIO']).copy()

    # 2. COMBUSTÍVEL
    # --- 2. LER ARQUIVO DE COMBUSTÍVEL ---
    print("Lendo arquivo de COMBUSTÍVEL (pode demorar)...")
    df_comb = pd.read_excel(os.path.join(input_folder, 'D_Frota_por_UF_Municipio_COMBUSTIVEL_Fevereiro_2026.xlsx'))

    # Pivotar combustíveis
    df_comb_pivot = df_comb.pivot_table(
        index=['UF', 'Município'], 
        columns='Combustível Veículo', 
        values='Qtd. Veículos', 
        aggfunc='sum'
    ).reset_index().fillna(0)

    # --- 3. PADRONIZAÇÃO E CRIAÇÃO DAS CHAVES ---
    mapa_uf = {
        'ACRE': 'AC', 'ALAGOAS': 'AL', 'AMAPA': 'AP', 'AMAZONAS': 'AM', 'BAHIA': 'BA',
        'CEARA': 'CE', 'DISTRITO FEDERAL': 'DF', 'ESPIRITO SANTO': 'ES', 'GOIAS': 'GO',
        'MARANHAO': 'MA', 'MATO GROSSO': 'MT', 'MATO GROSSO DO SUL': 'MS', 'MINAS GERAIS': 'MG',
        'PARA': 'PA', 'PARAIBA': 'PB', 'PARANA': 'PR', 'PERNAMBUCO': 'PE', 'PIAUI': 'PI',
        'RIO DE JANEIRO': 'RJ', 'RIO GRANDE DO NORTE': 'RN', 'RIO GRANDE DO SUL': 'RS',
        'RONDONIA': 'RO', 'RORAIMA': 'RR', 'SANTA CATARINA': 'SC', 'SAO PAULO': 'SP',
        'SERGIPE': 'SE', 'TOCANTINS': 'TO'
    }

    # Criando chaves no df_tipo
    df_tipo['municipio_limpo'] = df_tipo['MUNICIPIO'].apply(normalizar_nome)
    df_tipo['uf_limpa'] = df_tipo['UF'].astype(str).str.strip().str.upper()
    df_tipo['chave_merge'] = df_tipo['municipio_limpo'] + "_" + df_tipo['uf_limpa']

    # Criando chaves no df_comb
    df_comb_pivot['uf_sigla'] = df_comb_pivot['UF'].str.strip().str.upper().map(mapa_uf)
    df_comb_pivot['municipio_limpo'] = df_comb_pivot['Município'].apply(normalizar_nome)
    df_comb_pivot['chave_merge'] = df_comb_pivot['municipio_limpo'] + "_" + df_comb_pivot['uf_sigla']

    # --- 4. CONSOLIDAÇÃO (MERGE INTERNO) ---
    print("Unificando Tipos e Combustíveis pela chave_merge...")
    
    # Selecionamos apenas o que importa (DIESEL e FLEX são essenciais para utilitários)
    # Verificamos se as colunas existem para evitar erro
    cols_comb = ['chave_merge', 'DIESEL']
    if 'ALCOOL/GASOLINA' in df_comb_pivot.columns:
        df_comb_pivot.rename(columns={'ALCOOL/GASOLINA': 'FLEX'}, inplace=True)
        cols_comb.append('FLEX')

    df_consolidado = pd.merge(
        df_tipo, 
        df_comb_pivot[cols_comb], 
        on='chave_merge', 
        how='left'
    ).fillna(0)

    # --- 5. SALVAMENTO ---
    output_path = os.path.join(output_folder, 'renavam_fevereiro_processado.csv')
    df_consolidado.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"ETL do RENAVAM concluído!")
    print(f"Total de cidades na frota: {len(df_consolidado)}")
    print(f"Exemplo de chave criada: {df_consolidado['chave_merge'].iloc[0]}")

if __name__ == "__main__":
    processar_renavam()