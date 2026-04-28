# Etapa 3 — Construção de Modelo (K-Means Clustering)

## Preparação dos Dados

### Limpeza
- Removidos 44 municípios com `populacao=0` ou `TOTAL=0` (dados ausentes mascarados pelo fillna(0) do ETL)
- Dataset final: **5.527 municípios**

### Seleção de Features
As 6 features foram escolhidas com base na análise exploratória (Etapa 2) e nos objetivos do projeto:

| Feature | Justificativa | Transformação |
|:---|:---|:---|
| `target_perc_diesel` | Variável-alvo de interesse — composição diesel da frota | Nenhuma (já em %) |
| `target_perc_utilitarios` | Composição de utilitários da frota | Nenhuma (já em %) |
| `pib_agro_por_habitante` | Maior correlação com diesel (Pearson=0.43) | `log1p` (assimetria extrema) |
| `pib_per_capita` | Indicador de riqueza geral | `log1p` (assimetria) |
| `densidade_demografica` | Proxy de urbanização | `log1p` (assimetria extrema) |
| `presenca_rodovia_federal` | Polo logístico | Nenhuma (binária) |

### Normalização
Aplicamos `StandardScaler` (média=0, desvio=1) em todas as features. Isso é obrigatório para K-Means, pois o algoritmo utiliza distância euclidiana — variáveis com escalas maiores dominariam o cálculo de distância.

---

## Descrição do Modelo

### Algoritmo: K-Means

O K-Means é um algoritmo de **aprendizado não supervisionado** que particiona os dados em k grupos (clusters), minimizando a variância intra-cluster (inércia). O funcionamento é iterativo:

1. Inicializa k centróides aleatoriamente
2. Atribui cada observação ao centróide mais próximo (distância euclidiana)
3. Recalcula os centróides como a média dos pontos atribuídos
4. Repete os passos 2-3 até convergência (ou limite de iterações)

### Justificativa da Escolha
O K-Means foi selecionado como primeiro modelo porque:
- **Exploratório:** permite descobrir padrões ocultos sem necessidade de variável-alvo
- **Escalável:** eficiente para 5.527 observações
- **Interpretável:** cada cluster tem um centróide que representa o "município típico" do grupo
- **Alinhado com a literatura:** trabalhos como o CONBREPRO (2024) e Forsman (2024) utilizaram K-Means para segmentar frotas com sucesso

### Parâmetros Utilizados

| Parâmetro | Valor | Justificativa |
|:---|:---|:---|
| `n_clusters` | 4 | Determinado pelo Silhouette Score (melhor entre k=2 e k=10) |
| `random_state` | 42 | Reprodutibilidade dos resultados |
| `n_init` | 10 | Executa 10 inicializações diferentes e seleciona a melhor (mitiga sensibilidade à inicialização) |
| `max_iter` | 300 | Limite de iterações para convergência |

### Determinação do k Ótimo
Testamos k de 2 a 10 com dois métodos:
- **Método do Cotovelo:** observamos redução acentuada da inércia até k=4, com retornos decrescentes após
- **Silhouette Score:** k=4 obteve o maior score (0.2809), indicando melhor separação entre clusters

---

## Avaliação do Modelo

### Métricas Utilizadas

#### Métrica Principal: Silhouette Score
O **Silhouette Score** (0.2809) mede a qualidade da separação entre clusters:
- Varia de -1 (mal classificado) a +1 (perfeitamente classificado)
- Interpretação: **estrutura RAZOÁVEL** (entre 0.25 e 0.5) — os clusters têm alguma sobreposição, o que é esperado em dados socioeconômicos reais onde as fronteiras entre perfis municipais são graduais, não abruptas

#### Métrica Complementar: Inércia
A inércia final (16.430,20) representa a soma das distâncias quadradas de cada ponto ao centróide do seu cluster. O gráfico de cotovelo confirma que k=4 é um bom compromisso entre complexidade e compactação.

### Discussão dos Resultados

O modelo identificou **4 perfis automotivos** distintos no Brasil:

| Cluster | Nome | Municípios | % Diesel | PIB Agro/hab | Pop. Média | Características |
|:---|:---|:---|:---|:---|:---|:---|
| 0 | **Brasil Municipal Típico** | 2.689 (48,7%) | 7,73% | R$ 2.740 | 16.580 | Pequenos municípios, baixa vocação agro, diesel abaixo da média |
| 1 | **Brasil Agroindustrial** | 1.986 (35,9%) | 12,77% | R$ 18.573 | 12.066 | Alto PIB agro, alta dependência de diesel (RS, PR, SP, MG, SC) |
| 2 | **Brasil Metropolitano** | 741 (13,4%) | 8,06% | R$ 1.153 | 138.880 | Grandes cidades, alta densidade, frota diversificada (SP, MG, SC) |
| 3 | **Polos Logísticos** | 111 (2,0%) | 8,75% | R$ 3.414 | 276.498 | Municípios com rodovia federal, grandes centros distribuidores |

### Conexão com a Questão de Pesquisa

Os resultados **validam a hipótese central** do projeto: os indicadores socioeconômicos de um município atuam como preditores para a composição de sua frota. O Cluster 1 (Agroindustrial) concentra municípios onde o PIB agropecuário é 6,8x maior que a média nacional, e o percentual de diesel é 65% acima da média geral. Isso confirma que a vocação econômica do município determina diretamente o tipo de combustível predominante.

---

## Pipeline de Pesquisa e Análise de Dados

```
1. ESPECIFICAÇÃO DO PROBLEMA
   Questão: Como segmentar municípios por perfil de frota?
   Tipo: Aprendizado Não Supervisionado (Clusterização)

2. COLETA DE DADOS
   Fontes: SENATRAN (frota), IBGE (PIB/Censo), DNIT (rodovias)
   Granularidade: Municipal (5.571 municípios)

3. PRÉ-PROCESSAMENTO
   - Limpeza: remoção de municípios com pop=0 e TOTAL=0 (44 registros)
   - Feature Engineering: proporções (%), binarização DNIT
   - Transformação: log1p em variáveis com assimetria extrema
   - Normalização: StandardScaler (média=0, desvio=1)

4. SELEÇÃO DO MODELO
   Algoritmo: K-Means
   Justificativa: exploratório, escalável, interpretável

5. OTIMIZAÇÃO DE HIPERPARÂMETROS
   - Método do Cotovelo (Inércia vs k) para k de 2 a 10
   - Silhouette Score para cada k
   - k=4 selecionado (maior Silhouette = 0.2809)

6. TREINAMENTO E AVALIAÇÃO
   - Métrica principal: Silhouette Score = 0.2809 (razoável)
   - Métrica complementar: Inércia = 16.430,20
   - Convergência em 14 iterações

7. INTERPRETAÇÃO E DOCUMENTAÇÃO
   - 4 clusters: Municipal Típico, Agroindustrial, Metropolitano, Polos Logísticos
   - Validação da hipótese: vocação agro → mais diesel
   - Visualizações: scatter, boxplot, silhouette plot
```

---

## Código-Fonte

O notebook completo com todas as análises, visualizações e código está disponível em:

[`src/etapa3_modelo_kmeans.ipynb`](../src/etapa3_modelo_kmeans.ipynb)
