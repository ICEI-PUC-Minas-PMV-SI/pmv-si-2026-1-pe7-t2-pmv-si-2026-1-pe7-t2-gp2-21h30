# Projeto de Análise e Modelagem de Frota Veicular Brasileira (Etapa 2)

Este repositório contém a análise descritiva e exploratória dos dados unificados para a predição de demanda por veículos utilitários e motorização diesel nos municípios brasileiros.

## 📊 Conhecendo os Dados

Nesta seção, realizamos uma investigação detalhada para compreender a estrutura do dataset, detectar _outliers_ e avaliar as relações entre as variáveis socioeconômicas e a frota nacional.

### Análise Estatística Descritiva

Abaixo, apresentam-se as medidas de tendência central e dispersão calculadas após a limpeza e unificação dos dados.

| Variável                | Média    | Mediana  | Desvio Padrão | Insight Técnico                                                |
| :---------------------- | :------- | :------- | :------------ | :------------------------------------------------------------- |
| **População**           | 36.453   | 11.064   | 206.500       | Assimetria à direita extrema (presença de metrópoles).         |
| **Target % Diesel**     | 9,52%    | 8,98%    | 3,89          | Distribuição próxima à normal, ideal para modelagem.           |
| **PIB Agro per capita** | R$ 8.220 | R$ 2.829 | R$ 16.805     | Alta variabilidade; motor principal da demanda rural.          |
| **Rodovia Federal**     | 0,019    | 0,00     | 0,139         | Variável binária (apenas 2% dos municípios com malha federal). |

> **Nota sobre a Escala:** O `pib_per_capita` foi processado em escala de magnitude específica para manter a sensibilidade às variações decimais durante o cálculo de correlação de Pearson, garantindo que o modelo capture diferenças sutis de riqueza.

### Decisões Estratégicas de Engenharia de Dados

Durante o processo de ETL e Análise Exploratória, tomamos decisões críticas para garantir a qualidade do modelo:

1.  **O Ponto Cego da Infraestrutura:** Identificamos que a variável `km_terra_por_habitante` apresentava baixa densidade de dados (baixa variância). Optamos por substituí-la pela variável binarizada `presenca_rodovia_federal` (1 se o município possui registro no DNIT, 0 caso contrário), funcionando como um indicador de polo logístico.
2.  **Temporalidade do PIB:** Detectamos que a base IBGE de 2023 não dispõe do detalhamento setorial (VAB). Por isso, retrocedemos o corte temporal para **2021** para as colunas de Agro, Indústria e Serviços, mantendo a precisão analítica.

---

## 📈 Visualização e Achados

### Distribuição e Outliers (Histogramas e Boxplots)

As visualizações permitiram identificar padrões de concentração e anomalias:

- **Histogramas:** Confirmaram o perfil "Long Tail" (cauda longa) do Brasil, onde a maioria dos municípios é pequena, justificando o uso de taxas percentuais em vez de valores absolutos.
- **Boxplots:** Revelaram _outliers_ agressivos. Detectamos um município onde **76% da frota é composta por diesel**, um ponto de interesse extremo para o modelo preditivo.
- **Identificação de Gigantes:** O outlier populacional isolado representa a cidade de São Paulo, enquanto os extremos de PIB per capita representam cidades com polos industriais ou extrativistas.

### Relações entre Variáveis (Mapa de Calor)

A análise de correlação de Pearson revelou os seguintes achados:

- **Conexão Agro-Diesel (0.43):** Correlação positiva moderada. Validamos que o agronegócio é, de fato, o principal impulsionador da motorização diesel.
- **População x Diesel (-0.08):** Correlação negativa que confirma que grandes centros urbanos priorizam veículos flex/gasolina.
- **Poder Econômico (0.26):** O PIB per capita também influencia a frota diesel, mas em menor escala que a vocação agropecuária específica.

---

## 💻 Trechos de Código Relevantes

### 1. Binarização da Infraestrutura (ETL DNIT)

```python
# Transforma uma métrica esparsa em um indicador binário de polo logístico
df_infra['presenca_rodovia_federal'] = df_infra['Extensão'].apply(lambda x: 1 if x > 0 else 0)


# 2. Tratamento de Fallback Temporal (ETL PIB)
# Busca automática pelo ano mais recente com dados setoriais completos
anos_disponiveis = sorted(df_raw['Ano'].unique(), reverse=True)
for ano in anos_disponiveis:
    if df_ano.iloc[:, 32].sum() > 0: # Coluna do VAB Agropecuário
        ano_selecionado = ano # 2021 selecionado
        break

```

## 🛠️ Ferramentas Utilizadas

- **Linguagem**: Python 3.11
- **Bibliotecas de Dados**: Pandas, Numpy
- **Bibliotecas Gráficas**: Seaborn, Matplotlib
- **Ambiente**: Jupyter Notebook / VS Code

## 📁 Estrutura da Pasta src

No diretório src, incluímos os scripts completos:

[`ETL/script_etl_censo_demográfico.py`](ETL/script_etl_censo_demográfico.py): Tratamento de dados Populacional e densidade demográfica.

[`ETL/script_ETL_dnit.py`](ETL/script_ETL_dnit.py): Processamento de infraestrutura e binarização.

[`ETL/script_ETL_frota_RENAVAM.py`](ETL/script_ETL_dnit.py): Processamento de dados da Frota Brasileira

[`ETL/script_etl_PIB_municipios.py`](ETL/script_ETL_dnit.py): Tratamento de dados econômicos e escala.

[`ETL/Dados Tratados/unificador_final.py`](ETL/script_ETL_dnit.py): Script mestre de integração das bases.

[`analise_exploratoria.ipynb`](ETL/script_ETL_dnit.py): Notebook com as visualizações e estatísticas.

## Instalando as dependências

Para instalar as dependências basta digitar no terminal:

```Terminal
pip install -r requirements.txt
```
