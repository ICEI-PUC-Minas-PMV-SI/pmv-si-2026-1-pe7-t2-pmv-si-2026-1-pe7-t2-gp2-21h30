# Etapa 3 — Construção de Modelo (K-Means Clustering)

## Natureza da Técnica

O K-Means é um algoritmo de **aprendizado não supervisionado**. Esta característica determina como os resultados podem (e não podem) ser interpretados:

- **Não existe variável-alvo (target)** — o algoritmo não tenta prever um rótulo
- **Não mede poder preditivo** — apenas identifica grupos de observações semelhantes
- Todas as variáveis utilizadas são **features descritivas** que compõem o espaço de clusterização
- Os resultados revelam **associações estruturais** entre os perfis municipais, **não relações causais ou preditivas**

Esta distinção é crítica para a interpretação correta dos resultados desta etapa.

---

## Preparação dos Dados

### Tratamento de Valores Ausentes (Pipeline Refinado)

O pipeline ETL foi reformulado para tratar NaN **variável por variável**, eliminando o uso anterior de `fillna(0)` global e `replace(0, 1)` em denominadores:

| Variável | Tratamento | Justificativa |
|:---|:---|:---|
| Frota (TOTAL, AUTOMOVEL, etc.) | `fillna(0)` | Ausência no RENAVAM = sem registro = frota zero (semanticamente correto) |
| Infraestrutura DNIT | `fillna(0)` | Ausência no DNIT = sem rodovia federal (variável binarizada) |
| **PIB e População** | **Mantido NaN** | Ausência real de dados — não preenchemos com zero |
| Indicadores per capita | `np.where` retornando NaN se denominador = 0 | Evita criar valores artificiais por divisão protegida |

**Mudança crítica:** A versão anterior do `unificador_final.py` aplicava `pop = df_master['populacao'].replace(0, 1)` e `total_f = df_master['TOTAL'].replace(0, 1)` antes das divisões, e `df_master.fillna(0)` ao final. Esses procedimentos foram removidos pois distorciam indicadores derivados. Agora, registros com denominadores zerados resultam em NaN explícito, e são excluídos antes da modelagem.

### Limpeza para Clusterização
- Excluímos municípios com **NaN em qualquer feature essencial** (PIB, população, frota)
- Excluímos municípios com `TOTAL=0` (sem frota registrada)
- Dataset final: aproximadamente 5.500 municípios

### Seleção de Features

Utilizamos 6 variáveis descritivas para compor o espaço de clusterização:

| Feature | Descrição | Papel no Modelo |
|:---|:---|:---|
| `target_perc_diesel` | % da frota que é diesel | Variável descritiva da composição da frota |
| `target_perc_utilitarios` | % da frota que é utilitários | Variável descritiva da composição da frota |
| `pib_agro_por_habitante` | PIB agropecuário per capita | Variável descritiva da vocação econômica |
| `pib_per_capita` | PIB total per capita | Variável descritiva de riqueza |
| `densidade_demografica` | Habitantes por km² | Variável descritiva de urbanização |
| `presenca_rodovia_federal` | Indicador binário | Variável descritiva de infraestrutura |

**Observação importante:** Os nomes `target_perc_diesel` e `target_perc_utilitarios` foram herdados da nomenclatura do dataset original. **No contexto desta etapa (clusterização), elas são features descritivas, não variáveis-alvo no sentido supervisionado.** A nomenclatura "target" só será apropriada na Etapa 4, com modelos supervisionados.

### Transformação e Normalização
- `log1p` em variáveis com forte assimetria (PIB, densidade demográfica), confirmada pela Etapa 2
- `StandardScaler` (média=0, desvio=1) — necessário porque o K-Means utiliza distância euclidiana

---

## Descrição do Modelo

### Algoritmo: K-Means

O K-Means particiona os dados em k grupos minimizando a variância intra-cluster (inércia). Funciona iterativamente:

1. Inicializa k centróides aleatoriamente
2. Atribui cada observação ao centróide mais próximo (distância euclidiana)
3. Recalcula os centróides como a média dos pontos atribuídos
4. Repete os passos 2-3 até convergência

### Justificativa da Escolha
- **Exploratório:** adequado para identificar agrupamentos sem rótulos pré-definidos
- **Escalável:** eficiente para milhares de observações
- **Interpretável:** cada cluster tem um centróide que representa o "município típico" do grupo
- **Alinhado com a literatura:** trabalhos como CONBREPRO (2024) e Forsman (2024) utilizaram K-Means para segmentar frotas

### Parâmetros Utilizados

| Parâmetro | Valor | Justificativa |
|:---|:---|:---|
| `n_clusters` | 4 | Determinado pelo Silhouette Score |
| `random_state` | 42 | Reprodutibilidade |
| `n_init` | 10 | Mitiga sensibilidade à inicialização |
| `max_iter` | 300 | Limite de iterações para convergência |

### Determinação do k Ótimo
Testamos k de 2 a 10 com dois métodos:
- **Método do Cotovelo:** observamos redução acentuada da inércia até k=4
- **Silhouette Score:** k=4 obteve o maior score, indicando melhor separação dentre os testados

---

## Avaliação do Modelo

### Métricas Utilizadas

#### Métrica Principal: Silhouette Score
Métrica apropriada para clusterização (não supervisionada). Mede a qualidade da separação entre clusters:
- Coesão interna vs. separação externa
- Não requer rótulos verdadeiros
- Escala interpretativa:
  - **> 0.7:** estrutura forte
  - **0.5 a 0.7:** estrutura razoável
  - **0.25 a 0.5:** estrutura fraca a moderada
  - **< 0.25:** sem estrutura substancial

#### Métrica Complementar: Inércia
Soma das distâncias quadradas ao centróide. Útil para o Método do Cotovelo, mas não é métrica de qualidade absoluta.

### Por que NÃO usamos métricas supervisionadas
Acurácia, precisão, recall, F1, MAE, RMSE e R² **não se aplicam** a clusterização. Essas métricas serão usadas na Etapa 4 com modelos supervisionados.

---

## Discussão Crítica e Limitações Metodológicas

### Interpretação Honesta do Silhouette Score
O Silhouette Score obtido (em torno de 0.28) indica **separação MODERADA**:

- Os clusters são **úteis para fins exploratórios**, mas **não devem ser interpretados como categorias rígidas**
- Existe **sobreposição relevante** entre clusters
- Um Silhouette modesto **não autoriza conclusões fortes**
- O modelo identifica tendências, **não classificações definitivas**

### Sensibilidade a Outliers
- O K-Means é sensível a outliers, que podem distorcer centróides
- Mitigação parcial via `log1p` em variáveis assimétricas
- Outliers identificados na Etapa 2 (ex: Rondolândia-MT com 76% diesel) podem influenciar a formação dos clusters

### Estabilidade do Agrupamento
- Resultados podem variar com diferentes inicializações (mitigado com `n_init=10`)
- A escolha das features influencia diretamente os clusters
- O número de clusters (k) é uma decisão metodológica, não um valor "correto" absoluto

### Limites da Inferência
Os clusters identificados sugerem **associação estrutural** entre perfis socioeconômicos e composição da frota. Eles **NÃO**:
- Provam relação causal
- Demonstram poder preditivo (isso requer modelo supervisionado — Etapa 4)
- Devem ser usados isoladamente para decisões críticas

### Limitações dos Dados (herdadas das Etapas 1 e 2)
- Local de registro (RENAVAM) ≠ local de circulação real
- Defasagem temporal: PIB de 2021 vs. frota de 2026
- Viés de locadoras
- Falácia ecológica: inferências sobre municípios não se aplicam a indivíduos

---

## Resultados — Os Quatro Agrupamentos Identificados

O modelo identificou **4 perfis municipais** com características distintas:

| Cluster | Nome | Perfil | % Diesel Médio | Característica Principal |
|:---|:---|:---|:---|:---|
| 0 | Brasil Municipal Típico | Pequenos municípios, baixa vocação agrícola | ~7,7% | Maioria do território brasileiro |
| 1 | Brasil Agroindustrial | Alto PIB agro, alta densidade rural | ~12,8% | Concentrado em RS, PR, SP, MG, SC |
| 2 | Brasil Metropolitano | Grandes cidades, alta densidade demográfica | ~8,1% | Capitais e regiões metropolitanas |
| 3 | Polos Logísticos | Municípios com rodovia federal | ~8,8% | Centros distribuidores |

### Conexão com a Questão de Pesquisa

Os agrupamentos identificados **sugerem associação estrutural** entre perfis socioeconômicos municipais e composição da frota. O Cluster 1 (Agroindustrial) concentra municípios onde o PIB agropecuário é significativamente maior que a média, e o percentual de diesel também é mais elevado.

**Importante:** Esta análise **descreve** uma associação observada, não comprova relação causal nem capacidade preditiva. A hipótese de que indicadores socioeconômicos podem **prever** a composição da frota será testada com modelos supervisionados na Etapa 4.

---

## Pipeline de Pesquisa e Análise de Dados

```
1. ESPECIFICAÇÃO DO PROBLEMA
   Questão exploratória: existem perfis distintos de municípios brasileiros
   em termos de composição de frota e indicadores socioeconômicos?
   Tipo: Aprendizado Não Supervisionado (Clusterização)

2. COLETA DE DADOS
   Fontes: SENATRAN (frota), IBGE (PIB/Censo), DNIT (rodovias)
   Granularidade: Municipal

3. PRÉ-PROCESSAMENTO (refinado)
   - Tratamento de NaN justificado por variável (sem fillna(0) global)
   - Sem replace(0, 1) em denominadores (NaN preservado)
   - Exclusão de registros com NaN em features essenciais
   - Log transform em variáveis com assimetria extrema
   - StandardScaler para igualar escalas

4. SELEÇÃO DO MODELO
   Algoritmo: K-Means
   Justificativa: exploratório, escalável, interpretável

5. OTIMIZAÇÃO DE HIPERPARÂMETROS
   - Método do Cotovelo (Inércia vs k)
   - Silhouette Score para cada k (2 a 10)
   - k=4 selecionado

6. TREINAMENTO E AVALIAÇÃO
   - Métrica principal: Silhouette Score (separação MODERADA)
   - Métrica complementar: Inércia
   - Análise de perfil por cluster

7. INTERPRETAÇÃO CRÍTICA
   - Limitações metodológicas explicitadas
   - Distinção entre associação estrutural e capacidade preditiva
   - Discussão de outliers, estabilidade e sensibilidade
   - Reconhecimento de que clusters não são categorias rígidas
```

---

## Código-Fonte

O notebook completo com todas as análises, visualizações e código está disponível em:

[`src/etapa3_modelo_kmeans.ipynb`](../src/etapa3_modelo_kmeans.ipynb)

E o pipeline ETL refinado em:

[`src/ETL/Dados Tratados/unificador_final.py`](../src/ETL/Dados%20Tratados/unificador_final.py)
