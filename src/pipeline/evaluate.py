import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def calcular_metricas(y_real, y_pred):
    """Calcula métricas principais de regressão."""
    mae = mean_absolute_error(y_real, y_pred)
    mse = mean_squared_error(y_real, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_real, y_pred)
    return mae, mse, rmse, r2

def avaliar_modelos(modelos_treinados, X_test, y_test, features_nomes, output_img_dir):
    """
    Avalia cada modelo, gera tabela comparativa e exporta gráficos diagnósticos.
    """
    os.makedirs(output_img_dir, exist_ok=True)
    resultados = []
    
    # Configurar estilo dos gráficos
    sns.set_theme(style="whitegrid")
    
    # 1. Loop de avaliação dos modelos
    for nome, modelo in modelos_treinados.items():
        y_pred = modelo.predict(X_test)
        mae, mse, rmse, r2 = calcular_metricas(y_test, y_pred)
        
        resultados.append({
            "Modelo": nome,
            "MAE (Principal)": round(mae, 4),
            "MSE": round(mse, 4),
            "RMSE": round(rmse, 4),
            "R2 Score": round(r2, 4)
        })
        
        # Gerar gráficos específicos para cada modelo
        gerar_graficos_diagnostico(nome, y_test, y_pred, modelo, features_nomes, output_img_dir)
        
    df_comparacao = pd.DataFrame(resultados)
    df_comparacao = df_comparacao.sort_values(by="MAE (Principal)", ascending=True)
    
    return df_comparacao

def gerar_graficos_diagnostico(nome_modelo, y_real, y_pred, modelo, features_nomes, output_img_dir):
    """Gera gráficos de dispersão (Real vs Predito), resíduos e importância de features."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico 1: Real vs Predito
    axes[0].scatter(y_real, y_pred, alpha=0.4, color='teal', edgecolor='k', s=20)
    ideal_line = np.linspace(min(y_real), max(y_real), 100)
    axes[0].plot(ideal_line, ideal_line, 'r--', lw=2, label='Predição Perfeita')
    axes[0].set_xlabel('Valor Real (% Diesel)')
    axes[0].set_ylabel('Valor Predito (% Diesel)')
    axes[0].set_title(f'{nome_modelo}: Valores Reais vs. Preditos')
    axes[0].legend()
    
    # Gráfico 2: Resíduos
    residuos = y_real - y_pred
    axes[1].scatter(y_pred, residuos, alpha=0.4, color='purple', edgecolor='k', s=20)
    axes[1].axhline(0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Valor Predito (% Diesel)')
    axes[1].set_ylabel('Resíduo (Real - Predito)')
    axes[1].set_title(f'{nome_modelo}: Gráfico de Resíduos')
    
    plt.tight_layout()
    filename_diag = f"diag_{nome_modelo.lower().replace(' ', '_').replace('(', '').replace(')', '')}.png"
    plt.savefig(os.path.join(output_img_dir, filename_diag), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Gráfico 3: Importância das Features (se disponível)
    if hasattr(modelo, 'feature_importances_'):
        plt.figure(figsize=(10, 6))
        importancias = modelo.feature_importances_
        indices = np.argsort(importancias)[::-1]
        
        df_imp = pd.DataFrame({
            'Feature': [features_nomes[i] for i in indices],
            'Importancia': importancias[indices]
        })
        
        sns.barplot(data=df_imp.head(10), x='Importancia', y='Feature', hue='Feature', palette='viridis', legend=False)
        plt.title(f'Importância das Features (Top 10) - {nome_modelo}')
        plt.xlabel('Importância Relativa')
        plt.ylabel('Feature')
        plt.tight_layout()
        filename_imp = f"feature_importance_{nome_modelo.lower().replace(' ', '_').replace('(', '').replace(')', '')}.png"
        plt.savefig(os.path.join(output_img_dir, filename_imp), dpi=150, bbox_inches='tight')
        plt.close()
