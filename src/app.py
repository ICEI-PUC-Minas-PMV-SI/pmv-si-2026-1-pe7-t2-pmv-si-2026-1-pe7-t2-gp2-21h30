import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import joblib

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Preditor de Frota Diesel - Eixo 7",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Resolução de Caminhos Absolutos
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, 'ETL', 'Dados Tratados', 'Dados Unificados', 'dataset_final_modelagem.csv')
scaler_path = os.path.join(current_dir, 'models', 'scaler.joblib')
model_path = os.path.join(current_dir, 'models', 'model_xgboost.joblib')

# Estilização CSS Customizada (Aesthetics)
st.markdown("""
<style>
    /* Estilo geral */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Cores e degrade no titulo */
    .title-gradient {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Cards de Metricas */
    .metric-card {
        background-color: #f7fafc;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #0072FF;
        margin-bottom: 1rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #4a5568;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 2.2rem;
        color: #1a202c;
        font-weight: 700;
        margin-top: 5px;
    }
    
    /* Layout dos blocos de entrada */
    .section-header {
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
        margin-top: 15px;
        margin-bottom: 15px;
        color: #0072FF;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar os recursos do modelo em cache para alta performance
@st.cache_resource
def carregar_modelo_e_scaler():
    if not os.path.exists(scaler_path) or not os.path.exists(model_path):
        return None, None, "Erro: Arquivos do modelo não encontrados. Por favor, execute o pipeline de treinamento primeiro."
    try:
        scaler = joblib.load(scaler_path)
        model = joblib.load(model_path)
        return scaler, model, None
    except Exception as e:
        return None, None, f"Erro ao carregar o modelo: {str(e)}"

# Função para carregar os dados brutos de municípios em cache
@st.cache_data
def carregar_dados_municipios():
    if not os.path.exists(dataset_path):
        return None, "Erro: Base de dados final não encontrada. Verifique o caminho."
    try:
        df = pd.read_csv(dataset_path)
        # Filtros de limpeza aplicados na modelagem
        df = df[(df['populacao'] > 0) & (df['TOTAL'] > 0)]
        # Criar chave de exibição
        df['uf'] = df['uf'].fillna('')
        df['municipio_uf'] = df['municipio'] + " - " + df['uf']
        df = df.sort_values(by='municipio_uf')
        return df, None
    except Exception as e:
        return None, f"Erro ao carregar municípios: {str(e)}"

# Carregamento dos dados e modelos
scaler, model, err_model = carregar_modelo_e_scaler()
df_muni, err_muni = carregar_dados_municipios()

# Barra lateral para controle de dados (Autofill)
st.sidebar.markdown("### 🔍 Preenchimento Rápido")
st.sidebar.write("Escolha um município brasileiro real para carregar seus dados socioeconômicos e rodoviários correspondentes.")

muni_selecionado = None
if err_muni:
    st.sidebar.error(err_muni)
    autofill_active = False
else:
    opcoes = ["Preencher Manualmente (Em branco)"] + list(df_muni['municipio_uf'].unique())
    opcao_selecionada = st.sidebar.selectbox("Selecione o Município:", opcoes)
    
    if opcao_selecionada != "Preencher Manualmente (Em branco)":
        muni_selecionado = df_muni[df_muni['municipio_uf'] == opcao_selecionada].iloc[0]
        autofill_active = True
        st.sidebar.success(f"Dados de {muni_selecionado['municipio']} - {muni_selecionado['uf']} carregados!")
    else:
        autofill_active = False
        st.sidebar.info("Modo manual ativo. Insira os dados no formulário principal.")

# Cabeçalho Principal da Aplicação
st.markdown('<div class="title-gradient">Previsão da Frota Diesel nos Municípios Brasileiros</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Infere a porcentagem de veículos movidos a diesel na frota municipal com base em fatores geográficos e socioeconômicos do censo.</div>', unsafe_allow_html=True)

if err_model:
    st.error(err_model)
    st.stop()

# Definir as features que o modelo espera na ordem correta
FEATURES_ORDEM = [
    'populacao', 'area', 'densidade_demografica', 'vab_agro', 'vab_industria', 
    'vab_servicos', 'pib_per_capita', 'extensao_total_km', 'km_pavimentado', 
    'km_terra', 'presenca_rodovia_federal', 'pib_agro_por_habitante', 'km_terra_por_habitante'
]

# Inicializar valores padrão com base na seleção ou em valores medianos típicos
valores_iniciais = {}
if autofill_active and muni_selecionado is not None:
    for f in FEATURES_ORDEM:
        valores_iniciais[f] = muni_selecionado[f]
else:
    # Medianas aproximadas do dataset para iniciar com dados coerentes
    valores_iniciais = {
        'populacao': 11600.0,
        'area': 360.0,
        'densidade_demografica': 32.0,
        'vab_agro': 15000000.0,
        'vab_industria': 12000000.0,
        'vab_servicos': 45000000.0,
        'pib_per_capita': 21000.0,
        'extensao_total_km': 15.0,
        'km_pavimentado': 5.0,
        'km_terra': 10.0,
        'presenca_rodovia_federal': 0, # Não
        'pib_agro_por_habitante': 1500.0,
        'km_terra_por_habitante': 0.001
    }

# Formulário de Entradas Organizado
st.write("---")
st.markdown("### ✍️ Formulário de Variáveis Preditoras")
st.caption("Ajuste os valores abaixo para simular as características do município.")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🌍 Dados Socioeconômicos</div>', unsafe_allow_html=True)
    
    pop = st.number_input(
        "População Total (habitantes)",
        min_value=1, value=int(valores_iniciais['populacao']), step=100,
        help="População residente estimada do município."
    )
    
    area = st.number_input(
        "Área Municipal (km²)",
        min_value=0.1, value=float(valores_iniciais['area']), step=10.0,
        help="Área territorial do município em quilômetros quadrados."
    )
    
    # Calcular densidade demográfica dinamicamente como facilitador
    dens_sugestao = pop / area
    dens = st.number_input(
        "Densidade Demográfica (hab/km²)",
        min_value=0.01, value=float(valores_iniciais['densidade_demografica']), step=0.5,
        help=f"População dividida pela área municipal. Calculada dinamicamente: {dens_sugestao:.2f} hab/km²."
    )
    
    pib_pc = st.number_input(
        "PIB per capita (R$)",
        min_value=1.0, value=float(valores_iniciais['pib_per_capita']), step=100.0,
        help="Produto Interno Bruto municipal dividido pelo número de habitantes."
    )
    
    vab_ag = st.number_input(
        "VAB Agropecuária (R$)",
        min_value=0.0, value=float(valores_iniciais['vab_agro']), step=50000.0,
        help="Valor Adicionado Bruto do setor de Agropecuária a preços correntes."
    )
    
    vab_ind = st.number_input(
        "VAB Indústria (R$)",
        min_value=0.0, value=float(valores_iniciais['vab_industria']), step=50000.0,
        help="Valor Adicionado Bruto da Indústria a preços correntes."
    )
    
    vab_serv = st.number_input(
        "VAB Serviços (R$)",
        min_value=0.0, value=float(valores_iniciais['vab_servicos']), step=50000.0,
        help="Valor Adicionado Bruto do setor de Serviços a preços correntes (exclui administração pública)."
    )

with col2:
    st.markdown('<div class="section-header">🛣️ Infraestrutura e Rodovias</div>', unsafe_allow_html=True)
    
    ext_total = st.number_input(
        "Extensão Total de Rodovias (km)",
        min_value=0.0, value=float(valores_iniciais['extensao_total_km']), step=1.0,
        help="Soma das extensões pavimentadas e não pavimentadas dentro do município."
    )
    
    km_pav = st.number_input(
        "Extensão Pavimentada (km)",
        min_value=0.0, value=float(valores_iniciais['km_pavimentado']), step=1.0,
        help="Extensão de rodovias municipais, estaduais ou federais pavimentadas."
    )
    
    km_tr = st.number_input(
        "Extensão de Terra (km)",
        min_value=0.0, value=float(valores_iniciais['km_terra']), step=1.0,
        help="Extensão de estradas não pavimentadas (terra/cascalho)."
    )
    
    # Presença de Rodovia Federal como Selectbox (converte para 0 ou 1)
    pres_opcoes = {"Não": 0, "Sim": 1}
    opcao_pres = st.selectbox(
        "Presença de Rodovia Federal no Município?",
        options=list(pres_opcoes.keys()),
        index=0 if int(valores_iniciais['presenca_rodovia_federal']) == 0 else 1,
        help="Indica se existe alguma rodovia federal (BR) cruzando o território municipal."
    )
    pres_fed = pres_opcoes[opcao_pres]
    
    st.markdown('<div class="section-header">🌾 Indicadores Derivados</div>', unsafe_allow_html=True)
    
    pib_agro_pc_sugestao = vab_ag / pop
    pib_agro_pc = st.number_input(
        "PIB Agropecuário por Habitante (R$/hab)",
        min_value=0.0, value=float(valores_iniciais['pib_agro_por_habitante']), step=10.0,
        help=f"VAB Agro dividido pela população total. Calculado dinamicamente: R$ {pib_agro_pc_sugestao:.2f}/hab."
    )
    
    km_terra_pc_sugestao = km_tr / pop
    km_terra_pc = st.number_input(
        "Estradas de Terra por Habitante (km/hab)",
        min_value=0.0, value=float(valores_iniciais['km_terra_por_habitante']), format="%.6f", step=0.00001,
        help=f"Extensão de estradas de terra dividida pela população. Calculada dinamicamente: {km_terra_pc_sugestao:.6f} km/hab."
    )

# Ação de Predição
st.write("")
col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1, 1])
with col_btn_2:
    botao_predict = st.button("🚛 Executar Inferência Dinâmica", use_container_width=True, type="primary")

# Execução do cálculo se o botão for clicado ou se os dados mudarem
if botao_predict or (autofill_active and 'predicao' not in st.session_state):
    # Organizar dicionário na ordem estrita esperada
    dado_input = {
        'populacao': pop,
        'area': area,
        'densidade_demografica': dens,
        'vab_agro': vab_ag,
        'vab_industria': vab_ind,
        'vab_servicos': vab_serv,
        'pib_per_capita': pib_pc,
        'extensao_total_km': ext_total,
        'km_pavimentado': km_pav,
        'km_terra': km_tr,
        'presenca_rodovia_federal': pres_fed,
        'pib_agro_por_habitante': pib_agro_pc,
        'km_terra_por_habitante': km_terra_pc
    }
    
    # Criar DataFrame com apenas 1 linha
    df_pred = pd.DataFrame([dado_input])[FEATURES_ORDEM]
    
    # Aplicar o StandardScaler treinado
    df_pred_scaled = scaler.transform(df_pred)
    
    # Fazer a predição via XGBoost Regressor
    predicao = model.predict(df_pred_scaled)[0]
    
    # Salvar em sessão
    st.session_state['predicao'] = predicao
    st.session_state['dados_inferencia'] = dado_input
    
if 'predicao' in st.session_state:
    pred_final = st.session_state['predicao']
    # Evitar percentuais físicos absurdos devido à regressão estatística
    pred_final = max(0.0, min(100.0, pred_final))
    
    # Carregar média nacional se dados de municípios estiverem disponíveis para comparação
    avg_nacional = 11.5 # Média padrão aproximada caso falhe
    if not err_muni and df_muni is not None:
        avg_nacional = df_muni['target_perc_diesel'].mean()

    st.write("---")
    st.markdown("### 📊 Resultado da Inferência em Tempo de Execução")
    
    col_res1, col_res2 = st.columns([1, 1.5])
    
    with col_res1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Predição de Frota Diesel</div>
                <div class="metric-value">{pred_final:.4f}%</div>
                <p style="margin-top: 10px; font-size: 0.9rem; color: #4a5568;">
                    Porcentagem estimada de veículos a diesel no total da frota do município simulado.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        diff_avg = pred_final - avg_nacional
        cor_diff = "red" if diff_avg > 0 else "green"
        txt_diff = f"{abs(diff_avg):.2f}% acima" if diff_avg > 0 else f"{abs(diff_avg):.2f}% abaixo"
        
        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 5px solid #4a5568;">
                <div class="metric-label">Comparação com Média Nacional</div>
                <div class="metric-value" style="font-size: 1.8rem; color: {cor_diff};">{txt_diff}</div>
                <p style="margin-top: 10px; font-size: 0.9rem; color: #4a5568;">
                    Média de todos os municípios brasileiros analisados: <b>{avg_nacional:.2f}%</b> de diesel na frota.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_res2:
        # Gráfico de barras simples comparativo
        st.write("**Visualização do Perfil da Frota em Relação ao País:**")
        chart_data = pd.DataFrame({
            "Perfil": ["Município Simulado", "Média Nacional"],
            "Percentual Diesel (%)": [pred_final, avg_nacional]
        })
        st.bar_chart(chart_data, x="Perfil", y="Percentual Diesel (%)", color="#0072FF")
        
        # Diagnóstico descritivo inteligente baseado nas regras encontradas pela árvore de decisão e ensembles
        st.write("**Análise de Vocação Regional (Interpretação do Modelo):**")
        insumos = st.session_state['dados_inferencia']
        
        if insumos['pib_agro_por_habitante'] > 8000:
            st.warning("🌾 **Perfil Agropecuário Elevado:** O modelo detectou uma forte vocação para o Agronegócio por habitante. Municípios com esta característica demandam picapes, caminhonetes de grande porte e caminhões para escoamento de produção, elevando estatisticamente a proporção de motores diesel na frota.")
        elif insumos['populacao'] > 200000:
            st.info("🏢 **Perfil de Grande Metrópole:** População densa e grande centro urbano. Em metrópoles, predominam veículos de passeio individuais de passeio (flex/gasolina), o que reduz proporcionalmente a representatividade do diesel na frota total, mesmo com transporte coletivo ativo.")
        else:
            st.success("✅ **Perfil Regular:** Os indicadores socioeconômicos e de rodovias do município simulado alinham-se ao perfil médio dos municípios de pequeno a médio porte do interior, com distribuição equilibrada de frota.")
            
        if insumos['km_terra_por_habitante'] > 0.005:
            st.warning("🚜 **Alta Densidade de Estradas de Terra:** A grande presença de vias não pavimentadas por habitante sugere dependência de veículos utilitários robustos com tração 4x4 (geralmente movidos a diesel) para tráfego local.")

st.write("")
st.write("")
st.write("---")
# Rodapé técnico
st.markdown(
    """
    <div style="text-align: center; color: #a0aec0; font-size: 0.8rem; margin-top: 20px;">
        Projeto Integrador - Eixo 7 — Engenharia e Ciência de Dados | Deploy executado em servidor de computação em nuvem em tempo de execução via Docker e Streamlit.
    </div>
    """,
    unsafe_allow_html=True
)
