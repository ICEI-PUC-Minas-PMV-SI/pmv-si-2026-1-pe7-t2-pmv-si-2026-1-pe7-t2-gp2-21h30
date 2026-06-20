import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import joblib
import json
import requests
import plotly.express as px
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from streamlit_extras.stoggle import stoggle

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

# Estilização CSS Customizada
st.markdown("""
<style>
    /* Estilo geral */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Remover branding padrão do Streamlit, mantendo o menu principal (três pontinhos) */
    footer {visibility: hidden;}
    
    /* Customização da barra lateral esquerda */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        box-shadow: 2px 0 15px rgba(0,0,0,0.03) !important;
    }
    
    /* Estilização do Menu de Rádio da Barra Lateral (Menu Interativo) */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 10px !important;
        padding-top: 10px;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: var(--background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01) !important;
        transition: all 0.25s ease-in-out !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        border-color: #0072FF !important;
        background: var(--secondary-background-color) !important;
        transform: translateX(4px) !important; /* Micro-animação de movimento lateral */
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
        border-color: #0072FF !important;
        background: rgba(0, 114, 255, 0.12) !important;
        box-shadow: 0 4px 10px rgba(0, 114, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] span,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) span {
        color: #0072FF !important;
        font-weight: 600 !important;
    }
    
    /* Estilizar o container principal nativo do Streamlit como a nossa página flutuante */
    [data-testid="stAppViewBlockContainer"] {
        background-color: var(--background-color) !important;
        border-radius: 24px !important;
        padding: 40px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02) !important;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        margin-top: 30px !important;
        margin-bottom: 30px !important;
    }
    
    /* Degradê e estilo do título principal */
    .title-gradient {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 50%, #0045A5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.6rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Efeito de Vidro Fosco (Glassmorphism) nos Cards de Métricas */
    .metric-card {
        background: var(--secondary-background-color) !important;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        border-left: 6px solid #0072FF !important;
        margin-bottom: 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px); /* Elevação suave ao passar o mouse */
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.04);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-color) !important;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 2.3rem;
        color: var(--text-color) !important;
        font-weight: 700;
        margin-top: 5px;
    }
    
    /* Botões de Ação Personalizados (Estilo SaaS Premium) */
    .stButton > button {
        background: linear-gradient(135deg, #0072FF 0%, #0045A5 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.25) !important;
        transition: all 0.25s ease-in-out !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.35) !important;
        color: #ffffff !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Inputs de Número e Selectboxes Personalizados com foco ativo */
    div[data-testid="stNumberInput"] input {
        border-radius: 12px !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 10px 14px !important;
        font-size: 0.95rem !important;
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stNumberInput"] input:focus {
        border-color: #0072FF !important;
        box-shadow: 0 0 0 3px rgba(0, 114, 255, 0.15) !important;
    }
    
    div[data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        background-color: var(--background-color) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-baseweb="select"]:focus-within {
        border-color: #0072FF !important;
        box-shadow: 0 0 0 3px rgba(0, 114, 255, 0.15) !important;
    }
    
    /* Seções e Divisores */
    .section-header {
        border-bottom: 2px solid rgba(128, 128, 128, 0.15);
        padding-bottom: 6px;
        margin-top: 15px;
        margin-bottom: 15px;
        color: #0072FF;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Informações de Ajuda (Aba Sobre) */
    .info-box {
        background: var(--secondary-background-color) !important;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
    }
    .info-box-title {
        color: #0072FF;
        font-weight: 600;
        font-size: 1.15rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Badges de Perfil */
    .profile-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .profile-urbano {
        background-color: #E6FFFA;
        color: #319795;
        border: 1px solid #B2F5EA;
    }
    .profile-misto {
        background-color: #EBF8FF;
        color: #2B6CB0;
        border: 1px solid #BEE3F8;
    }
    .profile-agro {
        background-color: #FFFAF0;
        color: #DD6B20;
        border: 1px solid #FEEBC8;
    }
    
    /* Barra de progresso customizada */
    .progress-container {
        background-color: #edf2f7;
        border-radius: 8px;
        height: 10px;
        width: 100%;
        margin-top: 15px;
        margin-bottom: 15px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar os recursos do modelo em cache
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

# Função para carregar animação Lottie com timeout de segurança
@st.cache_data
def carregar_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Carregar dados, modelos e animação
scaler, model, err_model = carregar_modelo_e_scaler()
df_muni, err_muni = carregar_dados_municipios()
lottie_truck = carregar_lottieurl("https://assets5.lottiefiles.com/packages/lf20_V9t630.json")

if err_model:
    st.error(err_model)
    st.stop()

# Definição das features que o modelo espera na ordem correta
FEATURES_ORDEM = [
    'populacao', 'area', 'densidade_demografica', 'vab_agro', 'vab_industria', 
    'vab_servicos', 'pib_per_capita', 'extensao_total_km', 'km_pavimentado', 
    'km_terra', 'presenca_rodovia_federal', 'pib_agro_por_habitante', 'km_terra_por_habitante'
]

# --- MENU LATERAL DE NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### 🗺️ Navegação do Portal")
    pagina = option_menu(
        menu_title=None,
        options=["Apresentação", "Dados Reais", "Simulador"],
        icons=["house", "database", "sliders"],
        default_index=0,
        styles={
            "container": {
                "padding": "0px",
                "background-color": "transparent"
            },
            "icon": {
                "color": "#64748b",
                "font-size": "1.1rem"
            },
            "nav-link": {
                "font-size": "0.92rem",
                "text-align": "left",
                "margin": "4px 0px",
                "padding": "12px 16px",
                "border-radius": "8px",
                "color": "var(--text-color)",
                "font-family": "Outfit, sans-serif",
                "transition": "all 0.15s ease-in-out",
                "background-color": "transparent"
            },
            "nav-link-hover": {
                "background-color": "rgba(100, 116, 139, 0.08)"
            },
            "nav-link-selected": {
                "background-color": "rgba(0, 114, 255, 0.08)",
                "color": "#0072FF",
                "font-weight": "600"
            }
        }
    )

# --- REUSABLE FUNCTIONS FOR UI RENDERING ---

def renderizar_formulario(valores, disabled=False, prefix="", key_suffix=""):
    """Renderiza o formulário com as 13 variáveis preditoras, bloqueado ou livre."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🌍 Dados Socioeconômicos</div>', unsafe_allow_html=True)
        
        pop = st.number_input(
            "População Total (habitantes)",
            min_value=1, value=int(valores['populacao']), step=100,
            disabled=disabled, key=f"{prefix}_{key_suffix}_pop",
            help="População residente estimada do município."
        )
        
        area = st.number_input(
            "Área Municipal (km²)",
            min_value=0.1, value=float(valores['area']), step=10.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_area",
            help="Área territorial do município em quilômetros quadrados."
        )
        
        dens_sugestao = pop / area
        dens = st.number_input(
            "Densidade Demográfica (hab/km²)",
            min_value=0.01, value=float(valores['densidade_demografica']), step=0.5,
            disabled=disabled, key=f"{prefix}_{key_suffix}_dens",
            help=f"População dividida pela área municipal. Calculada dinamicamente: {dens_sugestao:.2f} hab/km²."
        )
        
        pib_pc = st.number_input(
            "PIB per capita (R$)",
            min_value=1.0, value=float(valores['pib_per_capita']), step=100.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_pib",
            help="Produto Interno Bruto municipal dividido pelo número de habitantes."
        )
        
        vab_ag = st.number_input(
            "VAB Agropecuária (R$)",
            min_value=0.0, value=float(valores['vab_agro']), step=50000.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_vab_ag",
            help="Valor Adicionado Bruto do setor de Agropecuária a preços correntes."
        )
        
        vab_ind = st.number_input(
            "VAB Indústria (R$)",
            min_value=0.0, value=float(valores['vab_industria']), step=50000.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_vab_ind",
            help="Valor Adicionado Bruto da Indústria a preços correntes."
        )
        
        vab_serv = st.number_input(
            "VAB Serviços (R$)",
            min_value=0.0, value=float(valores['vab_servicos']), step=50000.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_vab_serv",
            help="Valor Adicionado Bruto do setor de Serviços a preços correntes (exclui administração pública)."
        )

    with col2:
        st.markdown('<div class="section-header">🛣️ Infraestrutura e Rodovias</div>', unsafe_allow_html=True)
        
        ext_total = st.number_input(
            "Extensão Total de Rodovias (km)",
            min_value=0.0, value=float(valores['extensao_total_km']), step=1.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_ext",
            help="Soma das extensões pavimentadas e não pavimentadas dentro do município."
        )
        
        km_pav = st.number_input(
            "Extensão Pavimentada (km)",
            min_value=0.0, value=float(valores['km_pavimentado']), step=1.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_pav",
            help="Extensão de rodovias municipais, estaduais ou federais pavimentadas."
        )
        
        km_tr = st.number_input(
            "Extensão de Terra (km)",
            min_value=0.0, value=float(valores['km_terra']), step=1.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_terra",
            help="Extensão de estradas não pavimentadas (terra/cascalho)."
        )
        
        pres_opcoes = {"Não": 0, "Sim": 1}
        opcao_pres = st.selectbox(
            "Presença de Rodovia Federal no Município?",
            options=list(pres_opcoes.keys()),
            index=0 if int(valores['presenca_rodovia_federal']) == 0 else 1,
            disabled=disabled, key=f"{prefix}_{key_suffix}_fed",
            help="Indica se existe alguma rodovia federal (BR) cruzando o território municipal."
        )
        pres_fed = pres_opcoes[opcao_pres]
        
        st.markdown('<div class="section-header">🌾 Indicadores Derivados</div>', unsafe_allow_html=True)
        
        pib_agro_pc_sugestao = vab_ag / pop
        pib_agro_pc = st.number_input(
            "PIB Agropecuário por Habitante (R$/hab)",
            min_value=0.0, value=float(valores['pib_agro_por_habitante']), step=10.0,
            disabled=disabled, key=f"{prefix}_{key_suffix}_agro_pc",
            help=f"VAB Agro dividido pela população total. Calculado dinamicamente: R$ {pib_agro_pc_sugestao:.2f}/hab."
        )
        
        km_terra_pc_sugestao = km_tr / pop
        km_terra_pc = st.number_input(
            "Estradas de Terra por Habitante (km/hab)",
            min_value=0.0, value=float(valores['km_terra_por_habitante']), format="%.6f", step=0.00001,
            disabled=disabled, key=f"{prefix}_{key_suffix}_terra_pc",
            help=f"Extensão de estradas de terra dividida pela população. Calculada dinamicamente: {km_terra_pc_sugestao:.6f} km/hab."
        )

    return {
        'populacao': pop, 'area': area, 'densidade_demografica': dens,
        'vab_agro': vab_ag, 'vab_industria': vab_ind, 'vab_servicos': vab_serv,
        'pib_per_capita': pib_pc, 'extensao_total_km': ext_total, 'km_pavimentado': km_pav,
        'km_terra': km_tr, 'presenca_rodovia_federal': pres_fed,
        'pib_agro_por_habitante': pib_agro_pc, 'km_terra_por_habitante': km_terra_pc
    }

def exibir_resultados(pred_final, avg_nacional, insumos):
    """Exibe o painel estético e compreensível de resultados e drivers econômicos."""
    # 1. Classificação do Perfil
    if pred_final < 8.0:
        perfil_nome = "Perfil Urbano & Passeio 🚗"
        perfil_classe = "profile-urbano"
        perfil_cor = "#319795"
        perfil_desc = "Predomínio de veículos leves e motocicletas. Típico de metrópoles e polos comerciais urbanos onde o transporte individual e familiar é focado em carros flex ou gasolina."
    elif pred_final <= 15.0:
        perfil_nome = "Perfil Misto & Comercial 🚚"
        perfil_classe = "profile-misto"
        perfil_cor = "#2B6CB0"
        perfil_desc = "Distribuição equilibrada de frota. Comum em cidades de médio porte com tráfego urbano regular, transporte coletivo e distribuição logística moderada de mercadorias."
    else:
        perfil_nome = "Perfil Agrícola, Logístico ou de Carga 🚜"
        perfil_classe = "profile-agro"
        perfil_cor = "#DD6B20"
        perfil_desc = "Forte dependência de veículos pesados, caminhões e utilitários 4x4. Comum em polos agroindustriais, de mineração ou entroncamentos de frete de longa distância."

    # Tradução em proporção física simples
    if pred_final > 0:
        proporcao_v = int(round(100 / pred_final))
        proporcao_texto = f"Aproximadamente 1 em cada {proporcao_v} veículos"
    else:
        proporcao_texto = "Nenhum veículo (0%)"
        
    diff_avg = pred_final - avg_nacional
    cor_diff = "#E53E3E" if diff_avg > 0 else "#38A169"
    cor_diff_bg = "#FED7D7" if diff_avg > 0 else "#C6F6D5"
    txt_diff = f"{abs(diff_avg):.2f}% acima" if diff_avg > 0 else f"{abs(diff_avg):.2f}% abaixo"

    st.write("---")
    st.markdown("### 📊 Resultado da Inferência em Tempo de Execução")
    
    col_res1, col_res2 = st.columns([1, 1.5])
    
    with col_res1:
        # Card consolidado com Glassmorphism e Barra de Progresso
        st.markdown(
            f"""
            <div class="metric-card">
                <span class="profile-badge {perfil_classe}">{perfil_nome}</span>
                <div class="metric-label">Diesel na Frota Estimada</div>
                <div class="metric-value">{pred_final:.4f}%</div>
                <div style="font-size: 1.02rem; font-weight: 600; color: var(--text-color); margin-top: 12px; margin-bottom: 6px;">
                    💡 O que isso significa?
                </div>
                <p style="margin: 0; font-size: 0.88rem; color: var(--text-color); opacity: 0.85; line-height: 1.5;">
                    Significa que <b>{proporcao_texto}</b> que rodam nas ruas deste município é movido a diesel.
                </p>
                <div class="progress-container">
                    <div class="progress-bar-fill" style="width: {pred_final}%; background-color: {perfil_cor};"></div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.88rem; color: var(--text-color); opacity: 0.85;">
                    <span style="background-color: {cor_diff_bg}; color: {cor_diff}; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 0.8rem;">{txt_diff}</span>
                    <span>da média nacional ({avg_nacional:.2f}%)</span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.info(f"💡 **Sobre o perfil:** {perfil_desc}")
        
    with col_res2:
        st.write("**Visualização do Perfil da Frota em Relação ao País:**")
        chart_data = pd.DataFrame({
            "Localidade": ["Este Município", "Média Nacional"],
            "Percentual Diesel (%)": [pred_final, avg_nacional]
        })
        
        fig = px.bar(
            chart_data,
            x="Localidade",
            y="Percentual Diesel (%)",
            color="Localidade",
            color_discrete_map={
                "Este Município": perfil_cor,
                "Média Nacional": "#a0aec0"
            },
            text="Percentual Diesel (%)"
        )
        fig.update_traces(
            texttemplate='%{text:.2f}%', 
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Diesel na Frota: %{y:.4f}%<extra></extra>'
        )
        fig.update_layout(
            showlegend=False,
            height=260,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif"),
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(title="Proporção Diesel (%)", showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[0, max(pred_final, avg_nacional) * 1.25])
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.write("**🔍 Por que o Modelo estimou este valor? (Análise Prática):**")
        
        # 1. População
        if insumos['populacao'] > 150000:
            desc_pop = f"População urbana de **{insumos['populacao']:,}** hab. Grandiosos centros urbanos diluem a fatia de diesel porque concentram milhões de carros de passeio comuns (flex/gasolina)."
            status_pop = "⬇️ Reduz o percentual"
        else:
            desc_pop = f"População pequena de **{insumos['populacao']:,}** hab. Cidades menores não possuem o volume massivo de carros de passeio leves das capitais, fazendo com que veículos utilitários e de carga apareçam mais."
            status_pop = "⬆️ Aumenta o peso relativo"
            
        # 2. PIB Agro
        vab_ag = insumos['vab_agro']
        vab_ind = insumos['vab_industria']
        vab_serv = insumos['vab_servicos']
        agro_percent = vab_ag / (vab_ag + vab_ind + vab_serv) if (vab_ag + vab_ind + vab_serv) > 0 else 0
        if insumos['pib_agro_por_habitante'] > 5000 or agro_percent > 0.15:
            desc_agro = f"Forte vocação para o Agronegócio (PIB Agro/hab de **R$ {insumos['pib_agro_por_habitante']:,.2f}**). Regiões agrícolas dependem de picapes 4x4 robustas, caminhonetes de carga e caminhões pesados para a lavoura."
            status_agro = "⬆️ Impulsiona fortemente"
        else:
            desc_agro = f"Baixa dependência direta do agronegócio local. A economia é predominantemente urbana (comércio e serviços), com pouca demanda por utilitários agropecuários pesados."
            status_agro = "➡️ Efeito neutro/baixo"
            
        # 3. Estradas de terra
        prop_terra = insumos['km_terra'] / insumos['extensao_total_km'] if insumos['extensao_total_km'] > 0 else 0
        if insumos['km_terra_por_habitante'] > 0.003 or prop_terra > 0.5:
            desc_terra = f"Alta proporção de estradas de terra (**{prop_terra*100:.1f}%** das vias). Estradas não pavimentadas exigem torque pesado, tração 4x4 e motores robustos a diesel para evitar atolamentos em dias de chuva."
            status_terra = "⬆️ Aumenta a necessidade"
        else:
            desc_terra = f"Malha rodoviária majoritariamente asfalto/pavimentada. Reduz a necessidade forçada de veículos utilitários 4x4 robustos para trafegar em estradas de terra no dia a dia."
            status_terra = "➡️ Efeito baixo"
            
        st.markdown(
            f"""
            *   **Tamanho do Município:** {status_pop}  
                <span style="font-size: 0.88rem; color: var(--text-color); opacity: 0.85;">{desc_pop}</span>
            *   **Vocação do Agronegócio:** {status_agro}  
                <span style="font-size: 0.88rem; color: var(--text-color); opacity: 0.85;">{desc_agro}</span>
            *   **Vias e Rodovias:** {status_terra}  
                <span style="font-size: 0.88rem; color: var(--text-color); opacity: 0.85;">{desc_terra}</span>
            """,
            unsafe_allow_html=True
        )

# --- FLUXO DE RENDERIZAÇÃO DAS PÁGINAS ---

# ----------------- 1. PÁGINA HOME -----------------
if pagina == "Apresentação":
    st.markdown('<div class="title-gradient">Portal de Previsão de Frota Diesel</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Análise Preditiva Regional baseada em Machine Learning para os Municípios Brasileiros</div>', unsafe_allow_html=True)
    
    col_welcome1, col_welcome2 = st.columns([3, 1])
    with col_welcome1:
        st.markdown("""
        <div style="background-color: rgba(0, 114, 255, 0.08); border-left: 6px solid #0072FF; padding: 20px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0, 114, 255, 0.03); height: 100%;">
            <h3 style="color: #0072FF; margin: 0 0 8px 0; font-size: 1.25rem; font-weight: 600;">🚚 Bem-vindo ao Portal de Previsão de Frota Diesel!</h3>
            <p style="color: var(--text-color); margin: 0; font-size: 0.95rem; line-height: 1.6; opacity: 0.9;">
                Este portal é um ambiente de <b>inferência dinâmica em tempo real</b> projetado para estimar a proporção de veículos movidos a diesel em frotas municipais. 
                Nosso modelo de Inteligência Artificial utiliza indicadores socioeconômicos e geográficos de domínio público (como PIB, população e malha rodoviária) para demonstrar como o perfil produtivo das regiões brasileiras determina sua demanda de transporte.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_welcome2:
        if lottie_truck:
            st_lottie(lottie_truck, height=150, key="truck_anim")
        else:
            st.markdown(
                """
                <div style="font-size: 5rem; text-align: center; padding-top: 15px;">
                    🚛
                </div>
                """,
                unsafe_allow_html=True
            )
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown(
            """
            <div class="info-box">
                <div class="info-box-title">🎯 Qual a intenção deste portal?</div>
                <p style="font-size: 0.92rem; color: var(--text-color); opacity: 0.85; line-height: 1.6; margin: 0;">
                    Demonstrar de forma prática como a <b>vocação produtiva, infraestrutura rodoviária e aspects demográficos</b> 
                    de cada município brasileiro ditam de forma direta o tipo de veículos e combustíveis demandados na região. 
                    Mostramos que é possível mapear e planejar a necessidade energética de transporte local utilizando apenas 
                    indicadores socioeconômicos públicos e de fácil acesso, sem depender de dados confidenciais de registro.
                </p>
            </div>
            <div class="info-box">
                <div class="info-box-title">❓ O que é o site e o que ele faz?</div>
                <p style="font-size: 0.92rem; color: var(--text-color); opacity: 0.85; line-height: 1.6; margin: 0;">
                    O portal é uma aplicação de **inferência dinâmica**. Ele carrega em memória um modelo estatístico de regressão 
                    previamente treinado. Quando novos dados socioeconômicos de um município são informados (reais ou simulados), 
                    a aplicação executa o modelo de machine learning instantaneamente e calcula qual a porcentagem estimada de veículos a diesel que fariam parte da frota local, sem precisar refazer nenhum treinamento técnico.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_info2:
        st.markdown(
            """
            <div class="info-box">
                <div class="info-box-title">📖 Como Navegar e Utilizar?</div>
                <p style="font-size: 0.92rem; color: var(--text-color); opacity: 0.85; line-height: 1.5; margin-bottom: 10px;">
                    Use o menu lateral esquerdo (<b>Navegação do Portal</b>) para acessar os recursos:
                </p>
                <ul style="font-size: 0.92rem; color: var(--text-color); opacity: 0.85; line-height: 1.6; padding-left: 20px; margin: 0;">
                    <li style="margin-bottom: 8px;">
                        <b>📊 Consulta de Dados Reais:</b> Permite selecionar um município brasileiro real. O formulário é preenchido e bloqueado (leitura), rodando a inferência automática para ver a previsão correspondente aos dados reais históricos do censo.
                    </li>
                    <li>
                        <b>🧪 Simulador de Cenários:</b> Um ambiente livre onde todos os campos estão abertos para edição. Você pode simular novos municípios, alterar valores econômicos e rodoviários e clicar em calcular para ver a estimativa do modelo.
                    </li>
                </ul>
            </div>
            <div class="info-box">
                <div class="info-box-title">🧠 A Ciência por trás do Modelo (Metodologia)</div>
                <p style="font-size: 0.92rem; color: var(--text-color); opacity: 0.85; line-height: 1.6; margin: 0;">
                    O motor preditivo foi construído utilizando dados de 5.527 municípios brasileiros coletados do **IBGE, SENATRAN e DNIT**. 
                    Treinamos um modelo baseado no algoritmo <b>XGBoost Regressor</b>, que alcançou um Erro Absoluto Médio (MAE) de apenas <b>2,12%</b> nos dados de teste.
                    Para evitar vazamentos de dados (<i>data leakage</i>), o algoritmo aprendeu as relações a partir de dados geográficos e econômicos puros, nunca tendo acesso a contagens de veículos na entrada do modelo.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------- 2. PÁGINA DADOS REAIS -----------------
elif pagina == "Dados Reais":
    st.markdown('<div class="title-gradient">Consulta de Dados Reais</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Veja as estatísticas demográficas de municípios reais e a estimativa do modelo correspondente</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏙️ Município em Análise")
    
    if err_muni:
        st.error(err_muni)
    else:
        opcao_muni = st.sidebar.selectbox("Selecione o Município:", df_muni['municipio_uf'].unique())
        muni_row = df_muni[df_muni['municipio_uf'] == opcao_muni].iloc[0]
        
        # Obter dicionário de valores reais
        valores_reais = {f: muni_row[f] for f in FEATURES_ORDEM}
        
        st.write("---")
        st.markdown("### 🔒 Variáveis Socioeconômicas Reais (Bloqueado)")
        st.caption("Os campos abaixo representam os dados reais do município e não podem ser editados nesta página.")
        stoggle(
            "ℹ️ Entenda o que significa cada variável do modelo",
            """
            • <b>População Total</b>: População residente estimada no município.<br>
            • <b>Área Municipal</b>: Extensão territorial em quilômetros quadrados.<br>
            • <b>Densidade Demográfica</b>: Habitantes por km² (calculado: População / Área).<br>
            • <b>PIB per capita</b>: Produto Interno Bruto médio do município dividido pelos habitantes.<br>
            • <b>VAB (Agropecuária, Indústria, Serviços)</b>: Valor Adicionado Bruto de cada setor de produção.<br>
            • <b>Extensão de Rodovias (Total, Pavimentada, Terra)</b>: Perfil em km da malha rodoviária municipal.<br>
            • <b>Presença de Rodovia Federal</b>: Se há passagens de rodovias federais (BR) no território.<br>
            • <b>PIB Agropecuário por Habitante</b>: VAB Agropecuário dividido pela População.<br>
            • <b>Estradas de Terra por Habitante</b>: Extensão de rodovias de terra dividida pela População.
            """
        )
        
        # Renderizar formulário DESABILITADO (Bloqueado para edição), usando chave dinâmica opcao_muni
        insumos = renderizar_formulario(valores_reais, disabled=True, prefix="real", key_suffix=opcao_muni)
        
        # Executar Inferência AUTOMATICAMENTE (sem botão)
        df_pred = pd.DataFrame([insumos])[FEATURES_ORDEM]
        df_pred_scaled = scaler.transform(df_pred)
        predicao = model.predict(df_pred_scaled)[0]
        pred_final = max(0.0, min(100.0, predicao))
        
        avg_nacional = df_muni['target_perc_diesel'].mean() if df_muni is not None else 11.5
        
        # Exibir o painel completo de resultados imediatamente
        exibir_resultados(pred_final, avg_nacional, insumos)

# ----------------- 3. PÁGINA SIMULADOR DE CENÁRIOS -----------------
elif pagina == "Simulador":
    st.markdown('<div class="title-gradient">Simulador de Cenários</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Crie municípios hipotéticos e simule o impacto de mudanças econômicas ou de vias na frota</div>', unsafe_allow_html=True)
    
    # Iniciar com valores padrão (medianas nacionais)
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
        'presenca_rodovia_federal': 0,
        'pib_agro_por_habitante': 1500.0,
        'km_terra_por_habitante': 0.001
    }
    
    st.write("---")
    st.markdown("### ✍️ Simulador de Variáveis Preditoras (Habilitado)")
    st.caption("Ajuste os valores abaixo para testar novos cenários e clique em calcular.")
    stoggle(
        "ℹ️ Entenda o que significa cada variável do modelo",
        """
        • <b>População Total</b>: População residente estimada no município.<br>
        • <b>Área Municipal</b>: Extensão territorial em quilômetros quadrados.<br>
        • <b>Densidade Demográfica</b>: Habitantes por km² (calculado: População / Área).<br>
        • <b>PIB per capita</b>: Produto Interno Bruto médio do município dividido pelos habitantes.<br>
        • <b>VAB (Agropecuária, Indústria, Serviços)</b>: Valor Adicionado Bruto de cada setor de produção.<br>
        • <b>Extensão de Rodovias (Total, Pavimentada, Terra)</b>: Perfil em km da malha rodoviária municipal.<br>
        • <b>Presença de Rodovia Federal</b>: Se há passagens de rodovias federais (BR) no território.<br>
        • <b>PIB Agropecuário por Habitante</b>: VAB Agropecuário dividido pela População.<br>
        • <b>Estradas de Terra por Habitante</b>: Extensão de rodovias de terra dividida pela População.
        """
    )
    
    # Renderizar formulário HABILITADO (Permite edição)
    insumos = renderizar_formulario(valores_iniciais, disabled=False, prefix="simulado", key_suffix="default")
    
    st.write("")
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1.2, 1])
    with col_btn_2:
        botao_predict = st.button("🚀 Executar Inferência Dinâmica", use_container_width=True, type="primary")

    if botao_predict:
        df_pred = pd.DataFrame([insumos])[FEATURES_ORDEM]
        df_pred_scaled = scaler.transform(df_pred)
        predicao = model.predict(df_pred_scaled)[0]
        pred_final = max(0.0, min(100.0, predicao))
        
        avg_nacional = df_muni['target_perc_diesel'].mean() if df_muni is not None else 11.5
        
        # Guardar predição do simulador em sessão
        st.session_state['pred_simulada'] = pred_final
        st.session_state['insumos_simulados'] = insumos
        
    if 'pred_simulada' in st.session_state:
        exibir_resultados(
            st.session_state['pred_simulada'], 
            df_muni['target_perc_diesel'].mean() if df_muni is not None else 11.5, 
            st.session_state['insumos_simulados']
        )

# Rodapé Técnico
st.write("")
st.write("")
st.write("---")
st.markdown(
    """
    <div style="text-align: center; color: #a0aec0; font-size: 0.8rem; margin-top: 20px;">
        Projeto Integrador - Eixo 7 — Engenharia e Ciência de Dados | Deploy executado em servidor de computação em nuvem em tempo de execução via Docker e Streamlit.
    </div>
    """,
    unsafe_allow_html=True
)
