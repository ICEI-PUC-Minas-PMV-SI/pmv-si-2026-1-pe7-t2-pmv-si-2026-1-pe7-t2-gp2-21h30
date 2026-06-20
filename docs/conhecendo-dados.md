# Conhecendo os Dados — Etapa 2

## Análise Descritiva e Exploratória da Frota Veicular Brasileira (RENAVAM)

**Unidade de análise:** Município (5.571 municípios brasileiros)  
**Dataset:** `dataset_final_modelagem.csv` — construído a partir da integração das bases SENATRAN, IBGE e DNIT via pipeline ETL.

---

## 1. Qualidade dos Dados e Tratamento de Valores Ausentes

Antes de iniciar a análise exploratória, realizamos uma auditoria de qualidade sobre o dataset unificado. O pipeline ETL aplicou as seguintes estratégias de tratamento:

| Base de Origem | Tratamento Aplicado | Justificativa |
|:---|:---|:---|
| RENAVAM (frota) | `fillna(0)` nas tabelas pivot de tipo/combustível | Ausência de registro = 0 veículos naquela categoria. Semanticamente correto. |
| DNIT (rodovias) | `fillna(0)` na extensão; binarização para `presenca_rodovia_federal` | Município sem registro no DNIT = sem rodovia federal. |
| IBGE (PIB) | Valores monetários ausentes retornam `0.0` | Poucos municípios afetados. Requer cautela na interpretação. |
| Censo (população) | `pd.to_numeric` com `errors='coerce'` | NaN em registros inválidos pode propagar para densidade demográfica. |
| Unificador | `fillna(0)` global ao final do merge | Garante ausência de NaN, mas pode mascarar dados ausentes em PIB e população. |

**Ponto de atenção:** Para variáveis de frota e infraestrutura, o valor zero é semanticamente correto (sem registro = sem veículos/rodovias). Para PIB e população, zero pode mascarar ausência real de dados. Identificamos poucos municípios com `populacao=0`, que serão excluídos na etapa de modelagem.

---

## 2. Medidas de Tendência Central e Dispersão

Estatísticas descritivas completas para as variáveis-chave do projeto:

| Variável | Contagem | Média | Mediana | Moda | Desvio Padrão | Variância | Q1 | Q3 | IQR | Amplitude | Coef. Variação (%) | Assimetria |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **populacao** | 5.571 | 36.453 | 11.064 | 2.946 | 206.500 | 4,26E+10 | 5.223 | 24.426 | 19.203 | 11.452.000 | 566,2% | Extrema direita |
| **pib_per_capita** | 5.571 | 3.053.921 | 2.023.352 | 809.043 | 4.082.023 | 1,66E+13 | 1.078.226 | 3.808.747 | 2.730.521 | 92.082.840 | 133,6% | Direita |
| **target_perc_diesel** | 5.571 | 9,52% | 8,98% | 0,0 | 3,89 | 15,19 | 6,90 | 11,57 | 4,67 | 76,08 | 40,9% | Moderada direita |
| **target_perc_utilitarios** | 5.571 | 0,76% | 0,61% | 0,0 | 0,61 | 0,37 | 0,37 | 0,97 | 0,60 | 7,49 | 80,7% | Direita |
| **pib_agro_por_habitante** | 5.571 | 8.220 | 2.829 | 0,0 | 16.805 | 2,82E+08 | 974 | 9.230 | 8.256 | 313.568 | 204,4% | Extrema direita |
| **presenca_rodovia_federal** | 5.571 | 0,019 | 0,00 | 0,0 | 0,139 | 0,019 | 0 | 0 | 0 | 1 | 703,3% | Binária |

### Interpretação da Assimetria

A comparação entre média e mediana revela forte assimetria em quase todas as variáveis:

- **População:** Média (36.453) é 3,3x maior que a mediana (11.064). Poucos municípios grandes (capitais e metrópoles) puxam a média para cima. O Brasil típico tem ~11 mil habitantes.
- **PIB per capita:** Razão média/mediana de 1,5x. Municípios com polos industriais ou extrativistas inflacionam a média.
- **% Diesel:** Distribuição mais próxima da normal (assimetria moderada), com a maioria dos municípios entre 5% e 15%. Ideal para modelagem por regressão.
- **PIB Agro por habitante:** Média (R$ 8.220) é 2,9x maior que a mediana (R$ 2.829). Poucos municípios altamente agrícolas dominam.

### Testes Estatísticos de Normalidade (Shapiro-Wilk)

Para fundamentar rigorosamente a escolha das correlações e dos algoritmos de aprendizado de máquina, aplicamos o teste de Shapiro-Wilk sobre uma amostra de 5.000 municípios (limite recomendado do teste). A hipótese nula ($H_0$) é de que os dados seguem uma distribuição normal. Se $p < 0,05$, rejeitamos $H_0$, atestando desvio da normalidade.

| Variável | Estatística W | p-value | Decisão ($H_0$) | Conclusão |
| :--- | :---: | :---: | :---: | :--- |
| `populacao` | 0,0963 | $1,81 \times 10^{-93}$ | Rejeita $H_0$ | Distribuição Não-Normal |
| `pib_per_capita` | 0,5124 | $1,32 \times 10^{-79}$ | Rejeita $H_0$ | Distribuição Não-Normal |
| `target_perc_utilitarios` | 0,7867 | $8,27 \times 10^{-63}$ | Rejeita $H_0$ | Distribuição Não-Normal |
| `target_perc_diesel` | 0,9062 | $3,87 \times 10^{-48}$ | Rejeita $H_0$ | Distribuição Não-Normal |
| `pib_agro_por_habitante` | 0,4480 | $2,64 \times 10^{-82}$ | Rejeita $H_0$ | Distribuição Não-Normal |

**Interpretação:** Todas as variáveis apresentam desvio estatisticamente significante da normalidade ($p < 0,001$). Isso exige o uso de coeficientes de correlação não-paramétricos (como o de Spearman) e justifica a escolha de modelos de Machine Learning baseados em árvores e conjuntos (como Random Forest e XGBoost), que tratam a assimetria e não-normalidade nativamente sem a necessidade de transformações rígidas de escala.


---

## 3. Análise de Variáveis Categóricas

### 3.1. Distribuição por Região

| Região | Municípios | % do Total |
|:---|:---|:---|
| Nordeste | ~1.794 | 32,2% |
| Sudeste | ~1.668 | 29,9% |
| Sul | ~1.191 | 21,4% |
| Centro-Oeste | ~467 | 8,4% |
| Norte | ~450 | 8,1% |

O Nordeste possui mais municípios, mas com frota média menor. O Sudeste, apesar de ter menos municípios, concentra a maior frota média por município.

### 3.2. Comparação Regional das Variáveis-Alvo

A análise por boxplots regionais revelou que:
- **% Diesel:** Centro-Oeste e Sul apresentam medianas mais altas (Sul com média de 12,15% e mediana de 11,86%; Centro-Oeste com média de 11,90% e mediana de 11,15%), consistente com a vocação agropecuária dessas regiões, enquanto o Nordeste tem a menor taxa (média de 7,88% e mediana de 7,40%).
- **% Utilitários:** Centro-Oeste se destaca (média de 0,80%), reforçando a relação entre economia agrícola e demanda por veículos utilitários.

### Teste de Significância de Diferenças Regionais (Kruskal-Wallis)

Para certificar que as diferenças regionais na distribuição do percentual de diesel no Brasil são estatisticamente significativas (e não mero ruído de amostragem), aplicamos o teste não-paramétrico de Kruskal-Wallis. A hipótese nula ($H_0$) é que a distribuição da proporção de diesel na frota é a mesma em todas as 5 macro-regiões brasileiras.

- **Estatística H de Kruskal-Wallis:** 1352,6081
- **p-value:** $1,3052 \times 10^{-291}$
- **Conclusão:** Como o $p$-value é extremamente menor que 0,05 ($p < 0,001$), **rejeitamos a hipótese nula**. Existem diferenças regionalmente significativas e estatisticamente comprovadas na composição da frota de veículos leves a diesel entre as regiões do país, corroborando a necessidade de os modelos de ML utilizarem features regionais e contextuais.


---

## 4. Distribuição das Variáveis (Histogramas)

Os histogramas com curvas KDE e linhas de média/mediana confirmaram:

- **Perfil "Long Tail" (cauda longa):** A maioria dos municípios brasileiros é pequena. Variáveis como população e PIB possuem forte concentração à esquerda, com poucos valores extremos à direita (metrópoles e polos econômicos). Isso justifica o uso de **proporções (%)** em vez de valores absolutos na modelagem.
- **Target % Diesel:** Distribuição mais equilibrada, com pico entre 6% e 12%. Adequada para modelos de regressão sem necessidade de transformação logarítmica.

![Histogramas](./img/Distribuicao_Histogramas.png)

---

## 5. Detecção de Outliers com Critérios Estatísticos

Aplicamos dois métodos objetivos:

1. **Regra do IQR:** Outlier = valor fora do intervalo [Q1 - 1.5\*IQR, Q3 + 1.5\*IQR]
2. **Z-Score:** Outlier = valor com |z| > 3 (mais de 3 desvios padrão da média)

### Classificação dos Outliers Identificados

| Tipo | Exemplo | Tratamento |
|:---|:---|:---|
| **Outlier esperado por escala** | São Paulo (maior frota absoluta) | Usar proporções (%) resolve. Não é anomalia. |
| **Outlier real / anomalia** | Rondolândia-MT (76% diesel) | Município de fronteira agrícola isolado. Manter e monitorar impacto no modelo. |
| **Dado ausente mascarado** | Municípios com populacao=0 | Excluir da modelagem — resultado do fillna(0) no merge. |
| **Viés de registro** | Sedes de locadoras (ex: BH) | Frota registrada ≠ frota circulante. Limitação documentada. |

![Boxplots](./img/Outliers_Boxplots.png)

---

## 6. Análise de Correlação (Pearson e Spearman)

Calculamos ambos os coeficientes para capturar relações lineares (Pearson) e monotônicas (Spearman):

### Principais Achados e Significância Estatística das Correlações

Calculamos os coeficientes de correlação linear (Pearson) e monotônica de ranking (Spearman), juntamente com seus respectivos $p$-values, para avaliar o impacto das variáveis explicativas na proporção de frota diesel (`target_perc_diesel`):

| Variável Relacionada vs. % Diesel | Pearson ($r$) | p-value (Pearson) | Spearman ($\rho$) | p-value (Spearman) | Decisão e Interpretação |
|:---|:---:|:---:|:---:|:---:|:---|
| **PIB Agro por Habitante** | 0,4264 | $5,47 \times 10^{-245}$ | 0,5253 | $0,00$ (p < 1e-300) | **Significativo (Forte Positiva):** A atividade agropecuária per capita é a principal força indutora da frota diesel municipal. |
| **PIB per Capita** | 0,2644 | $8,68 \times 10^{-90}$ | 0,3851 | $1,89 \times 10^{-196}$ | **Significativo (Moderada Positiva):** A riqueza geral do município aumenta a taxa de diesel, porém com menor impacto do que a vocação agrícola. |
| **População** | -0,0825 | $6,84 \times 10^{-10}$ | -0,2694 | $2,82 \times 10^{-93}$ | **Significativo (Fraca Negativa):** Cidades muito populosas apresentam menor taxa de diesel, priorizando frotas flex e urbanas. |
| **Densidade Demográfica** | -0,1300 | $1,98 \times 10^{-22}$ | -0,3331 | $1,80 \times 10^{-144}$ | **Significativo (Moderada Negativa):** Áreas altamente adensadas e urbanizadas apresentam menor proporção de diesel. |

**Conclusões Importantes:**
- **Significância:** Todos os relacionamentos possuem p-values extremamente próximos de $0,00$ ($p < 0,05$), provando que as correlações são estatisticamente significativas e representam associações reais.
- **Não-Linearidade das Relações:** Em todos os casos, a correlação de Spearman ($\rho$) em módulo é substancialmente mais alta do que a de Pearson ($r$). Isso demonstra que a dinâmica da motorização diesel se comporta de maneira não-linear em relação aos indicadores municipais, fornecendo uma justificativa metodológica clara para a escolha de algoritmos baseados em árvores e conjuntos (como Random Forest e XGBoost) em vez de modelos de regressão linear.


![Heatmap de Correlação](./img/Matriz_Correlação_Heatmap.png)

### Scatter Plots

Gráficos de dispersão complementam a análise de correlação, permitindo visualizar a forma da relação (linear, exponencial, clusters). Os scatter plots de PIB Agro vs % Diesel evidenciam uma nuvem com tendência positiva, mas com dispersão significativa — sugerindo que variáveis adicionais (como região ou infraestrutura) são necessárias para explicar a variabilidade.

---

## 7. Considerações Éticas e LGPD

### 7.1. Conformidade com a LGPD
Os dados do SENATRAN e IBGE são estritamente públicos e agregados no nível municipal. Não contêm PII (CPF, placa, chassi, nome de proprietário), eliminando risco de reidentificação.

### 7.2. Risco de Falácia Ecológica
As correlações encontradas são entre **indicadores municipais**, não entre indivíduos. O correto é: *"municípios com alto PIB agropecuário tendem a ter maior proporção de diesel"*, e **não** *"pessoas ricas do agro compram diesel"*.

### 7.3. Risco de Estigmatização Regional
As disparidades Norte/Nordeste vs. Sul/Sudeste refletem condições socioeconômicas estruturais. Resultados devem ser comunicados sem juízos de valor sobre regiões.

### 7.4. Viés de Registro
Municípios-sede de locadoras possuem frotas desproporcionais. Isso deve ser explicitado na discussão dos resultados para evitar recomendações comerciais enviesadas.

---

## 8. Preparação para a Etapa 3

### 8.1. Variáveis-Alvo Definidas
- `target_perc_diesel` — para regressão supervisionada
- `target_perc_utilitarios` — para regressão supervisionada
- Clusters municipais — para K-Means (não supervisionado)

### 8.2. Features Candidatas
| Feature | Justificativa | Transformação |
|:---|:---|:---|
| `pib_agro_por_habitante` | Maior correlação com target (0.43) | Normalização |
| `pib_per_capita` | Indicador de riqueza geral | Normalização |
| `populacao` | Proxy de urbanização | Log transform |
| `densidade_demografica` | Indicador urbano/rural | Normalização |
| `presenca_rodovia_federal` | Polo logístico (binária) | Sem transformação |

### 8.3. Pré-processamento Necessário
- Excluir municípios com `populacao=0` (dados ausentes)
- Aplicar log transform em variáveis com assimetria extrema
- Normalizar features para K-Means (sensível a escala)
- Split treino/teste (70/30 ou 80/20)

### 8.4. Hipóteses a Testar
1. Municípios com maior PIB agropecuário per capita terão maior % de diesel
2. K-Means separará "Brasis Automotivos" com perfis de frota distintos
3. Random Forest superará Regressão Linear por capturar não-linearidades

---

## Ferramentas Utilizadas

- **Linguagem:** Python 3.11
- **Bibliotecas de Dados:** Pandas, NumPy, SciPy
- **Bibliotecas Gráficas:** Seaborn, Matplotlib
- **Ambiente:** Jupyter Notebook / VS Code

## Estrutura da Pasta src

| Arquivo | Descrição |
|:---|:---|
| [`ETL/script_etl_censo_demográfico.py`](../src/ETL/script_etl_censo_demográfico.py) | Tratamento de dados populacionais e densidade demográfica |
| [`ETL/script_ETL_dnit.py`](../src/ETL/script_ETL_dnit.py) | Processamento de infraestrutura e binarização |
| [`ETL/script_ETL_frota_RENAVAM.py`](../src/ETL/script_ETL_frota_RENAVAM.py) | Processamento de dados da frota brasileira |
| [`ETL/script_etl_PIB_municipios.py`](../src/ETL/script_etl_PIB_municipios.py) | Tratamento de dados econômicos |
| [`ETL/Dados Tratados/unificador_final.py`](../src/ETL/Dados%20Tratados/unificador_final.py) | Script mestre de integração das bases |
| [`analise_exploratoria.ipynb`](../src/analise_exploratoria.ipynb) | Notebook com visualizações e estatísticas |

## Instalação

```bash
pip install -r requirements.txt
```
