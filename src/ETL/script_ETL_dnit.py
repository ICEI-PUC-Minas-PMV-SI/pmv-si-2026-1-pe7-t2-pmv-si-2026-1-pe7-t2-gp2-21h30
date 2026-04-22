import pandas as pd
import os
import unicodedata

# Função de Normalização (Padronizada para todos os scripts)
def normalizar_nome(txt):
    if pd.isna(txt): return ""
    # Remove parênteses e limpa espaços
    txt = str(txt).split('(')[0].strip().upper()
    # Remove acentos
    nfkd_form = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def processar_snv():
    print("Iniciando ETL do SNV (DNIT) - Fevereiro 2026...")
    file_path = '../Dados/SNV_202602A.xls'
    
    # Lendo o arquivo Excel com tratamento de erros para garantir a leitura mesmo que haja problemas com o motor padrão
    try:
        df_snv = pd.read_excel(file_path, sheet_name='TABELA SNV', skiprows=2)
    except Exception:
        df_snv = pd.read_excel(file_path, sheet_name='TABELA SNV', skiprows=2, engine='xlrd')

    # 1. Limpeza de colunas e nomes (removendo espaços extras nos nomes das colunas)
    df_snv.columns = [c.strip() for c in df_snv.columns]
    df_snv = df_snv.dropna(subset=['UF', 'Código'])

    # 2. TRATAMENTO: Converter Extensão de string para float
    if df_snv['Extensão'].dtype == 'object':
        df_snv['Extensão'] = df_snv['Extensão'].astype(str).str.replace(',', '.').str.strip()
    
    df_snv['Extensão'] = pd.to_numeric(df_snv['Extensão'], errors='coerce').fillna(0)

    # 4. Pavimentado vs Terra
    df_snv['Superfície'] = df_snv['Superfície'].fillna('OUTROS').str.strip().str.upper()
    is_pav = df_snv['Superfície'].str.contains('PAV', na=False)
    df_snv['km_pavimentado'] = df_snv['Extensão'].where(is_pav, 0)
    df_snv['km_terra'] = df_snv['Extensão'].where(~is_pav, 0)

    # 4. CRIAÇÃO DA CHAVE DE INTEGRAÇÃO
    # Tratamos a 'Unidade Local' como o nome do município
    col_mun = 'Município' if 'Município' in df_snv.columns else 'Unidade Local'
    df_snv['municipio_limpo'] = df_snv[col_mun].apply(normalizar_nome)
    df_snv['uf_limpa'] = df_snv['UF'].str.strip().str.upper()

    # Criamos a chave que vai dar match com o Censo
    df_snv['chave_merge'] = df_snv['municipio_limpo'] + "_" + df_snv['uf_limpa']

    # 6. Agrupamento por Município
    # Soma todos os trechos federais que passam dentro da mesma cidade
    df_infra = df_snv.groupby(['chave_merge', 'uf_limpa', 'municipio_limpo']).agg({
        'Extensão': 'sum',
        'km_pavimentado': 'sum',
        'km_terra': 'sum'
    }).reset_index()

    # 7. FEATURE ENGINEERING: Variável Dummy (Agora na ordem correta!)
    # Se a soma da extensão for > 0, o município tem presença federal.
    df_infra['presenca_rodovia_federal'] = df_infra['Extensão'].apply(lambda x: 1 if x > 0 else 0)

    # Ajuste final de nomes
    df_infra.rename(columns={'uf_limpa': 'uf', 'Extensão': 'extensao_total_km'}, inplace=True)

    # 8. Salvamento
    output_folder = 'Dados Tratados'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'infraestrutura_snv_processado.csv')
    df_infra.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ ETL do SNV concluído!")
    print(f"Municípios com malha federal identificada: {len(df_infra)}")

if __name__ == "__main__":
    processar_snv()