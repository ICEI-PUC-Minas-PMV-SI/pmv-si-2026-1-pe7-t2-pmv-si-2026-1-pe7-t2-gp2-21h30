import os
import sys
import pandas as pd

# Adiciona o diretório atual do script ao path do Python para importações locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import preparar_dados
from models import inicializar_modelos
from evaluate import avaliar_modelos

def executar_pipeline(caminho_dados, alvo='target_perc_diesel'):
    print("=== INICIANDO O PIPELINE MODULAR DE MACHINE LEARNING (ETAPA 4) ===")
    
    # Resolvendo caminhos
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    diretorio_raiz = os.path.dirname(diretorio_atual) # src/
    diretorio_projeto = os.path.dirname(diretorio_raiz) # root
    
    output_img_dir = os.path.join(diretorio_projeto, 'docs', 'img')
    
    # 1. Carregamento e Pré-processamento
    print("\n[Passo 1/4] Preparando dados e aplicando Z-Score...")
    X_train, X_test, y_train, y_test, features_nomes = preparar_dados(
        caminho_csv=caminho_dados,
        target_col=alvo
    )
    print(f"-> Sucesso. Features preditoras utilizadas ({len(features_nomes)}):")
    print(f"   {list(features_nomes)}")
    print(f"-> Volume de Treino: {X_train.shape[0]} municípios")
    print(f"-> Volume de Teste: {X_test.shape[0]} municípios")
    
    # 2. Inicialização dos Modelos
    print("\n[Passo 2/4] Instanciando estimadores (Baseline + Ensembles)...")
    repositorio_modelos = inicializar_modelos()
    
    # 3. Treinamento
    print("\n[Passo 3/4] Treinando os modelos no conjunto de treinamento...")
    modelos_treinados = {}
    for nome, modelo in repositorio_modelos.items():
        print(f"   -> Treinando: {nome}...")
        modelo.fit(X_train, y_train)
        modelos_treinados[nome] = modelo
    print("-> Todos os modelos foram treinados.")
    
    # 4. Avaliação Comparativa
    print("\n[Passo 4/4] Avaliando modelos no conjunto de teste e gerando gráficos...")
    df_comparativo = avaliar_modelos(
        modelos_treinados=modelos_treinados,
        X_test=X_test,
        y_test=y_test,
        features_nomes=features_nomes,
        output_img_dir=output_img_dir
    )
    
    print("\n" + "=" * 60)
    print("=== PAINEL COMPARATIVO DE DESEMPENHO (Ordenado por MAE) ===")
    print("=" * 60)
    print(df_comparativo.to_string(index=False))
    print("=" * 60)
    print(f"\n[INFO] Graficos de diagnostico salvos com sucesso em: {output_img_dir}\n")
    
    # Salvar tabela de métricas em CSV para referência futura no notebook
    caminho_tabela = os.path.join(diretorio_raiz, 'tabela_comparacao_etapa4.csv')
    df_comparativo.to_csv(caminho_tabela, index=False)
    
    return modelos_treinados

if __name__ == "__main__":
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_dados_padrao = os.path.join(
        os.path.dirname(diretorio_atual),
        'ETL', 'Dados Tratados', 'Dados Unificados', 'dataset_final_modelagem.csv'
    )
    executar_pipeline(caminho_dados_padrao)
