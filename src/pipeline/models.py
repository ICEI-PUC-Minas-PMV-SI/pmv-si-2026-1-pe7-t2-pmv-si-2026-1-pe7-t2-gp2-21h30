from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def inicializar_modelos(random_state=42):
    """
    Centraliza a inicialização dos modelos de Machine Learning.
    Essa estrutura permite adicionar ou substituir algoritmos facilmente no pipeline.
    """
    modelos = {
        "Baseline (Decision Tree)": DecisionTreeRegressor(
            max_depth=5,
            random_state=random_state
        ),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=random_state,
            n_jobs=-1
        ),
        "XGBoost Regressor": XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=random_state,
            n_jobs=-1
        )
    }
    return modelos
