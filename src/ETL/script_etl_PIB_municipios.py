import pandas as pd
import os
import unicodedata

# 1. Função de Normalização Padronizada
def normalizar_nome(txt):
    if pd.isna(txt): return ""
    # Remove parênteses e limpa espaços
    txt = str(txt).split('(')[0].strip().upper()
    # Remove acentos e caracteres especiais
    nfkd_form = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def limpar_valor_monetario(valor, eh_per_capita=False):
    if pd.isna(valor): return 0.0
    v = str(valor).strip().replace('.', '') # Remove ponto de milhar
    v = v.replace(',', '.') # Troca vírgula por ponto decimal
    
    try:
        resultado = float(v)
        # Se for a coluna AN (per capita) e o valor veio sem a vírgula tratada, pode ser que seja um valor inteiro sem formatação, então tentamos dividir por 100 para ajustar
        return resultado
    except:
        return 0.0
    
def processar_pib():
    print("🚀 Iniciando ETL do PIB (Versão Robusta - 2023)...")
    # 1. Configuração de caminhos
    input_path = '../Dados/PIB dos Municípios - base de dados 2010-2023.xlsx'
    output_folder = 'Dados Tratados'
    output_path = os.path.join(output_folder, 'pib_processado.csv')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Carregamento dos dados
    print("Carregando base do PIB (IBGE)...")
    df_pib_raw = pd.read_excel(input_path, sheet_name='PIB dos Municípios')

    # Filtrar o ano mais recente
    # Procuramos o ano mais recente onde a coluna AG (índice 32) não seja zero
    print("🔍 Buscando ano mais recente com dados setoriais completos...")

    # Ordenamos pelos anos mais recentes primeiro
    anos_disponiveis = sorted(df_pib_raw['Ano'].unique(), reverse=True)
    
    ano_selecionado = None
    for ano in anos_disponiveis:
        df_ano = df_pib_raw[df_pib_raw['Ano'] == ano]
        # Verifica se a soma do Agro (coluna 32) nesse ano é maior que zero
        if df_ano.iloc[:, 32].apply(limpar_valor_monetario).sum() > 0:
            ano_selecionado = ano
            break
    
    if ano_selecionado:
        print(f"✅ Ano selecionado para análise técnica: {ano_selecionado}")
        df_pib = df_pib_raw[df_pib_raw['Ano'] == ano_selecionado].copy()
    else:
        print("❌ Erro: Não foram encontrados dados setoriais em nenhum ano.")
        return

    # 3. MAPEAMENTO POR ÍNDICE (ILOC)
    # Coluna G(6)=Código, H(7)=Nome, E(4)=UF, AG(32)=Agro, AH(33)=Ind, AI(34)=Serv, AN(39)=PIB per capita
    print("🧹 Extraindo colunas por posição física...")

    df_final = pd.DataFrame()
    df_final['codigo'] = df_pib.iloc[:, 6].astype(str).str.replace('.0', '', regex=False)
    df_final['municipio_nome'] = df_pib.iloc[:, 7]
    df_final['uf'] = df_pib.iloc[:, 4].astype(str).str.strip().str.upper()


    # Tratamento numérico direto nas posições AG, AH, AI e AN
    print("🧹 Tratando valores numéricos...")

    df_final['vab_agro'] = df_pib.iloc[:, 32].apply(limpar_valor_monetario)
    df_final['vab_industria'] = df_pib.iloc[:, 33].apply(limpar_valor_monetario)
    df_final['vab_servicos'] = df_pib.iloc[:, 34].apply(limpar_valor_monetario)
    df_final['pib_per_capita'] = df_pib.iloc[:, 39].apply(lambda x: limpar_valor_monetario(x, eh_per_capita=True))


    # 6. CRIAÇÃO DA CHAVE DE INTEGRAÇÃO
    df_final['municipio_limpo'] = df_final['municipio_nome'].apply(normalizar_nome)
    df_final['chave_merge'] = df_final['municipio_limpo'] + "_" + df_final['uf']


    # 5. VERIFICAÇÃO FINAL
    soma_agro = df_final['vab_agro'].sum()
    print(f"✅ Soma VAB Agro: {soma_agro:,.2f}")
    
    if soma_agro == 0:
        print("⚠️ ALERTA: A soma continua zero. Verifique se a aba 'PIB dos Municípios' começa na coluna A.")
        # Debug: Imprime o que tem na coluna 32 da primeira linha
        print(f"DEBUG: Valor na primeira linha (coluna 32): {df_pib.iloc[0, 32]}")

    os.makedirs('Dados Tratados', exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"ETL concluído! {len(df_final)} municípios processados.")

if __name__ == "__main__":
    processar_pib()