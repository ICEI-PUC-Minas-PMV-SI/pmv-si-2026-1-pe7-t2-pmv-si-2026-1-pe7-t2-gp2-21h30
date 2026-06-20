import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def preparar_dados(caminho_csv, target_col='target_perc_diesel', test_size=0.2, random_state=42):
    """
    Carrega o dataset final, aplica filtros de limpeza, isola IDs e colunas da frota
    para evitar vazamento de dados (data leakage), e aplica padronização nas features.
    
    Parâmetros:
    -----------
    caminho_csv : str -> Caminho para o arquivo CSV do dataset unificado.
    target_col : str -> Nome da variável-alvo (default: 'target_perc_diesel').
    test_size : float -> Proporção do conjunto de teste (default: 0.2).
    random_state : int -> Semente de aleatoriedade para divisão amostral.
    
    Retorna:
    --------
    X_train_scaled, X_test_scaled, y_train, y_test, list(features_nomes)
    """
    # 1. Carregar os dados
    df = pd.read_csv(caminho_csv)
    
    # 2. Limpeza: Remover registros com população = 0 ou frota total = 0 (dados inválidos)
    df = df[(df['populacao'] > 0) & (df['TOTAL'] > 0)]
    
    # 3. Definição de colunas de identificação e metadados
    colunas_identificacao = ['codigo', 'municipio', 'uf', 'municipio_limpo', 'chave_merge']
    
    # 4. Definição de colunas de frota (para prevenção estrita de Data Leakage)
    # Se mantivermos estas variáveis, o modelo aprenderá uma relação matemática direta
    # (ex: % diesel = DIESEL / TOTAL * 100) em vez de capturar relações socioeconômicas.
    colunas_frota = [
        'TOTAL', 'AUTOMOVEL', 'CAMINHONETE', 'MOTOCICLETA', 'UTILITARIO', 
        'DIESEL', 'FLEX', 'target_perc_utilitarios', 'target_perc_diesel'
    ]
    
    # 5. Isolar features socioeconômicas e geográficas
    colunas_remover = list(set(colunas_identificacao + colunas_frota))
    
    # Features preditoras (X) e Rótulo (y)
    X = df.drop(columns=colunas_remover, errors='ignore')
    y = df[target_col]
    
    # 6. Imputação de nulos residuais via mediana (garantia estatística)
    X = X.fillna(X.median())
    y = y.fillna(y.median())
    
    features_nomes = X.columns
    
    # 7. Divisão Treino e Teste (Holdout)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # 8. Padronização Estatística (Z-Score)
    # IMPORTANTE: O scaler ajusta a escala (fit) APENAS nos dados de treino
    # para evitar contaminação (data leakage) e apenas transforma (transform) o teste.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, list(features_nomes)

if __name__ == "__main__":
    # Teste rápido do script
    import os
    diretorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_dados = os.path.join(diretorio_raiz, 'ETL', 'Dados Tratados', 'Dados Unificados', 'dataset_final_modelagem.csv')
    if os.path.exists(caminho_dados):
        X_train, X_test, y_train, y_test, features = preparar_dados(caminho_dados)
        print(f"Sucesso! Shape de X_train: {X_train.shape}")
        print(f"Features preditoras utilizadas ({len(features)}): {features}")
    else:
        print(f"Caminho não encontrado para teste: {caminho_dados}")
