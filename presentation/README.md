# Apresentação da Solução

Este documento apresenta o resumo geral do projeto desenvolvido ao longo do semestre, o link para o vídeo de apresentação final e o roteiro detalhado utilizado para a gravação.

---

## 📽️ Vídeo de Apresentação Final
Assista à nossa apresentação final de no máximo 15 minutos, cobrindo o escopo do projeto, a metodologia, a demonstração prática da ferramenta no ar e nossas conclusões:

👉 **[Link para o Vídeo de Apresentação (YouTube / Drive)](https://drive.google.com/file/d/1aJDJLxG071sRavxqpUsGrVhzOPcaHEdP/view?usp=sharing)** *(Substitua este link com a URL do seu vídeo gravado)*

---

## 📋 Resumo Geral do Trabalho Desenvolvido

Nosso projeto investiga a variabilidade regional do mercado automotivo brasileiro, focando em como características socioeconômicas e geográficas dos municípios moldam a composição de suas frotas de veículos.

### 1. Contexto e Coleta de Dados (Etapa 1 e 2)
*   **Problema de Pesquisa:** Como estimar a proporção de veículos movidos a diesel em cada município sem depender de dados confidenciais ou de emplacamentos em tempo real, utilizando apenas dados públicos de infraestrutura e demografia?
*   **Origem dos Dados:** Unificamos três grandes bases de dados públicas a nível municipal:
    *   **SENATRAN (RENAVAM):** Dados consolidados de frotas por município divididos por tipo de combustível (Gasolina, Álcool, Flex, Diesel).
    *   **IBGE:** Indicadores socioeconômicos (população, área, PIB per capita, VAB por setor produtivo).
    *   **DNIT:** Extensões de malha rodoviária federal, estadual e municipal (pavimentada e não pavimentada).
*   **Desafios de ETL:** Realizamos a limpeza de registros inconsistentes (municípios fictícios ou com população nula), unificação de nomes através de chaves do IBGE e tratamento de nulos residuais via imputação por mediana.

### 2. Modelagem e Aprendizado de Máquina (Etapa 3 e 4)
*   **Prevenção de Vazamento (Data Leakage):** Para garantir o rigor científico, removemos estritamente todas as features de frota (como o total de veículos ou número absoluto de carros), mantendo apenas as 13 variáveis socioeconômicas e geográficas puras como preditores.
*   **Algoritmos Testados:**
    *   *Baseline:* Árvore de Decisão Regressora.
    *   *Ensembles:* Random Forest Regressor e XGBoost Regressor.
*   **Métrica de Avaliação Principal:** Escolhemos o **MAE (Mean Absolute Error - Erro Absoluto Médio)** para evitar que municípios que funcionam como outliers reais de registro (sedes de grandes locadoras com frotas artificiais gigantescas) distorcessem o aprendizado dos algoritmos.
*   **Resultado Comparativo (Conjunto de Teste):**
    *   **XGBoost Regressor (Campeão):** MAE de **2,1286%** e $R^2$ de **0,3456**.
    *   *Random Forest:* MAE de 2,1364% e $R^2$ de 0,3349.
    *   *Baseline (Decision Tree):* MAE de 2,2493% e $R^2$ de 0,2976.

### 3. Solução em Produção (Etapa 5)
*   **Painel Interativo (Streamlit):** Desenvolvemos uma interface web em Python que carrega o modelo treinado. Ela possui campos para entrada manual de dados e um seletor de municípios reais que preenche os dados socioeconômicos automaticamente para facilitar os testes.
*   **Deploy em Nuvem (Render):** O aplicativo foi conteinerizado com Docker e está rodando publicamente de forma estável no Render:  
    👉 **[https://frota-diesel-eixo7.onrender.com/](https://frota-diesel-eixo7.onrender.com/)**

---

## 🎯 Principais Conclusões Obtidas
1.  **Influência Socioeconômica Regional:** O coeficiente de determinação $R^2$ de 34,56% demonstra estatisticamente que mais de um terço da variabilidade da frota a diesel é explicada exclusivamente pela vocação econômica da região, comprovando o impacto direto do agronegócio e densidade demográfica na frota local.
2.  **Eficiência Computacional:** A modelagem matemática provou que a inferência do XGBoost consome pouquíssimo recurso computacional (~5 ms por execução), permitindo que a aplicação seja executada de forma escalável em máquinas simples e gratuitas na nuvem.
3.  **Transparência e Ética:** Ao utilizar dados agregados e públicos, o projeto cumpre com todas as diretrizes da LGPD, mitigando vieses individuais e evitando a falácia ecológica.
