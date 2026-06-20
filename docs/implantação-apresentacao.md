# Etapa 5 — Implantação e Apresentação da Solução

Este documento detalha o processo de planejamento, avaliação de capacidade, implantação da aplicação preditiva em ambiente de nuvem (produção) e a estrutura para a apresentação final do projeto.

---

## 1. Avaliação Comparativa de Provedores em Nuvem

Para escolher a melhor plataforma de nuvem para hospedar nossa solução baseada em Docker e Streamlit, avaliamos os três principais provedores (AWS, Azure e Google Cloud) além de uma solução de Plataforma como Serviço (Render) para testes e demonstrações sem custos operacionais.

| Critério de Comparação | Amazon Web Services (AWS) | Microsoft Azure | Google Cloud Platform (GCP) | Render (PaaS Selecionada) |
| :--- | :--- | :--- | :--- | :--- |
| **Serviço Avaliado** | AWS EC2 (Máquina Virtual) ou ECS + Fargate (Containers) | Azure VM ou Azure Container Apps | Compute Engine ou Google Cloud Run | Render Web Services (Hospedagem Docker) |
| **Escalabilidade** | Altíssima. Auto Scaling Groups com base em regras de uso de CPU/RAM. | Altíssima. Escalonamento automático integrado a nível de container. | Altíssima. Escalonamento horizontal ultrarrápido (escala para zero). | Média. Escalonamento horizontal fácil por painel web, mas manual no plano grátis. |
| **Monitoramento** | Nativo com AWS CloudWatch (métricas de CPU, rede e alarmes). | Nativo com Azure Monitor e Log Analytics. | Nativo com Google Cloud Monitoring e Cloud Logging. | Logs consolidados integrados em tempo de execução e gráficos de CPU/RAM. |
| **Custos Acadêmicos** | Free Tier disponível (t2.micro por 12 meses), mas requer cartão no cadastro. | Free Tier de $200 para estudantes, mas requer validação institucional ativa. | Créditos de teste grátis, mas com expiração rígida. | **Totalmente Gratuito** (plano Free para Web Services), sem riscos fiscais. |
| **Complexidade de Deploy**| Alta. Exige configuração de VPC, Security Groups, SSH e Nginx. | Média-Alta. Exige familiaridade com o CLI do Azure ou painel complexo. | Média. Cloud Run possui facilidade para deploy via gcloud CLI. | **Baixíssima.** Deploy automático e integrado diretamente ao repositório GitHub. |

### Justificativa de Escolha:
Para fins do escopo acadêmico do projeto e garantia de um link público e funcional para a banca examinadora, optou-se pela implantação no **Render**. 
- O Render roda sua infraestrutura sobre a nuvem da **AWS**, oferecendo suporte nativo à execução de arquivos `Dockerfile`.
- O deploy ocorre de forma contínua (CI/CD): qualquer commit enviado para a branch `main` do GitHub dispara o build automático da imagem do container, que é publicado de imediato.
- Oferece isolamento completo da aplicação e nos livra de custos inesperados que poderiam surgir com o uso de chaves e instâncias esquecidas em grandes provedores comerciais.
- *Nota: Na seção 3, descrevemos o desenho de arquitetura correspondente para um deploy comercial escalável em instâncias AWS EC2.*

---

## 2. Planejamento e Avaliação da Capacidade Operacional

O dimensionamento de recursos de computação, armazenamento e rede baseia-se em modelagem matemática e simulação do perfil de carga esperado.

### A. Modelagem Matemática de Filas (M/M/1)

Utilizamos a **Teoria de Filas** clássica com um único servidor (M/M/1) para simular o comportamento de tempo de resposta da aplicação de inferência dinâmica sob carga moderada e pico:

*   **$\lambda$ (Taxa de Chegada):** Média estimada de **2 requisições por segundo** ($\lambda = 2\text{ req/s}$) em momentos de tráfego de uso de alunos e avaliadores.
*   **$\mu$ (Taxa de Serviço):** Velocidade de processamento do servidor.
    *   A inferência do modelo XGBoost leva em média $5\text{ ms}$ ($0,005\text{ s}$).
    *   Considerando a transformação dos dados via `StandardScaler`, a orquestração do Streamlit e o overhead de rede interna do container, estimamos um tempo médio de serviço de **$50\text{ ms}$ por requisição** ($0,05\text{ s}$).
    *   Portanto, a capacidade de atendimento do servidor é de $\mu = \frac{1}{0,05} = 20\text{ requisições/segundo}$.

#### Cálculo de Métricas com Tráfego Normal ($\lambda = 2$):

1.  **Fator de Utilização do Servidor ($\rho$):**
    $$\rho = \frac{\lambda}{\mu} = \frac{2}{20} = 0,10 \text{ (ou 10\% de uso de CPU/Recursos)}$$
2.  **Probabilidade do Servidor Estar Ocioso ($P_0$):**
    $$P_0 = 1 - \rho = 1 - 0,10 = 0,90 \text{ (ou 90\% do tempo ocioso)}$$
3.  **Tempo Médio de Resposta no Sistema ($W$):**
    $$W = \frac{1}{\mu - \lambda} = \frac{1}{20 - 2} = \frac{1}{18} \approx 0,0556 \text{ s} \approx 55,6 \text{ ms}$$
    O tempo médio de resposta de $55,6\text{ ms}$ garante uma experiência de usuário instantânea e fluida.

#### Simulação de Estresse / Pico ($\lambda = 15$ requisições/segundo):

1.  **Fator de Utilização ($\rho$):**
    $$\rho = \frac{15}{20} = 0,75 \text{ (75\% de uso do servidor)}$$
2.  **Tempo Médio de Resposta no Sistema ($W$):**
    $$W = \frac{1}{\mu - \lambda} = \frac{1}{20 - 15} = \frac{1}{5} = 0,20 \text{ s} = 200 \text{ ms}$$
    Mesmo sob tráfego severo de concorrência ativa (15 usuários clicando simultaneamente no mesmo segundo), o tempo de resposta permanece em $200\text{ ms}$, muito abaixo do limite de SLA aceitável de $2.000\text{ ms}$ ($2\text{ s}$). A arquitetura de instância única é, portanto, matematicamente estável para a demanda do projeto.

---

### B. Dimensionamento de Recursos de Hardware (Sizing)

Com base no comportamento computacional da pilha Python + Streamlit + XGBoost, definimos as seguintes especificações mínimas e recomendadas:

#### 1. Memória RAM (Sizing Estático e Dinâmico):
*   **SO Slim (Linux Debian/Alpine):** ~100 MB
*   **Runtime Python + Streamlit Server:** ~150 MB
*   **Dependências de Ciência de Dados (Pandas, Scikit-Learn, XGBoost):** ~120 MB
*   **Arquivos do Modelo (`.joblib` em cache):** ~10 MB
*   **Buffer para Sessões de Usuários Concorrentes:** ~100 MB
*   **Total Estimado:** ~480 MB.
*   **Escolha:** A especificação de **512 MB de RAM** (oferecida pelo Render Free e por containers do GCP Cloud Run) ou **1 GB de RAM** (AWS `t2.micro` Free Tier) atende perfeitamente a demanda sem risco de estouro de memória (Out-Of-Memory).

#### 2. Capacidade de Processamento (CPU):
*   Como a inferência matemática do XGBoost é baseada em caminhos de árvores pré-calculados e executada em poucas milissegundos, **1 vCPU** (processador compartilhado ou dedicado) é mais do que suficiente para suportar a carga de trabalho sem causar lentidão de concorrência.

#### 3. Armazenamento em Disco:
*   A imagem Docker compilada ocupa aproximadamente **500 MB** de espaço em disco (Python Slim + bibliotecas instaladas + dados do censo para autofill + código).
*   **Escolha:** O disco padrão associado às instâncias (como o volume EBS básico da AWS de **8 GB gp3**) cobre de sobra o espaço necessário.

#### 4. Banda de Rede (Data Transfer):
*   Tamanho inicial do carregamento da aplicação (arquivos JS, CSS, fontes e HTML): ~1,8 MB.
*   Tamanho de dados de tráfego por predição (JSON leve via Websocket): ~10 KB.
*   Para um tráfego de **1.000 acessos por mês**, o consumo estimado de saída é:
    $$\text{Tráfego Mensal} = 1.000 \times 1,8\text{ MB} + 1.000 \times 5 \text{ (predições)} \times 10\text{ KB} \approx 1,85\text{ GB/mês}$$
    Esse valor está amplamente inserido nas franquias gratuitas oferecidas pelos provedores (que variam de 10 GB a 100 GB mensais).

---

## 3. Configuração do Ambiente e Implantação Prática

### A. Link de Produção Publicado
A aplicação em produção está disponível publicamente para testes e inferência dinâmica através do link:
👉 **[Painel de Inferência de Frota Diesel - Produção Render](https://frota-diesel-eixo7.onrender.com)** *(Link Demonstrativo)*

---

### B. Arquitetura Recomendada para Deploy Comercial em Nuvem (AWS)

Caso o sistema precise ser implantado em ambiente comercial produtivo robusto na AWS, a topologia recomendada é a seguinte:

1.  **Rede e Segurança (VPC):**
    *   Criação de uma **VPC** (Virtual Private Cloud) com uma sub-rede pública para acesso externo e uma sub-rede privada para o container.
    *   **Internet Gateway** acoplado à VPC para permitir a entrada de tráfego na porta HTTP/HTTPS.
    *   **Security Group:**
        *   *Inbound:* Liberar apenas portas `80` (HTTP) e `443` (HTTPS) para o público (`0.0.0.0/0`), e porta `22` (SSH) restrita ao IP administrativo.
2.  **Servidor de Aplicação (Instância EC2):**
    *   Instância **AWS EC2 t3.micro** (1 vCPU, 1 GB RAM) rodando Ubuntu Server.
    *   Instalação do Docker e do Docker-Compose na VM.
    *   Execução do container Streamlit na porta interna `8501`.
3.  **Proxy Reverso e Criptografia (Nginx + Let's Encrypt):**
    *   Instalação do **Nginx** na máquina servidora atuando como proxy reverso, encaminhando requisições da porta pública `80/443` para a porta local `8501` do Docker.
    *   Configuração do certificado SSL gratuito gerado pelo **Certbot (Let's Encrypt)** para tráfego seguro (HTTPS).

---

### C. Guia de Reprodução da Implantação (Local ou Nuvem)

#### Passo 1: Construção da Imagem Docker
No diretório onde se localiza o `Dockerfile` (pasta `src/`), execute o comando de build:
```bash
docker build -t frota-diesel-app -f src/Dockerfile src/
```

#### Passo 2: Execução do Container Localmente
Inicie o container mapeando a porta padrão do Streamlit:
```bash
docker run -d -p 8501:8501 --name painel-frota frota-diesel-app
```
A aplicação estará acessível localmente no endereço: `http://localhost:8501`.

---

## 4. Monitoramento do Desempenho e Alertas

Para garantir a confiabilidade operacional e detectar anomalias (como vazamentos de memória ou picos de tráfego de negação de serviço), estabeleceu-se a seguinte política de monitoramento e alertas:

### Métricas Críticas Monitoradas:
1.  **Uso de CPU (%):** Indica o esforço computacional do algoritmo.
2.  **Uso de Memória RAM (%):** Monitoramento contra vazamento de memória ou sobrecarga de sessões.
3.  **Latência de Resposta (SLA):** Tempo que leva para o usuário receber a predição.
4.  **Taxa de Erro HTTP 5xx (%):** Indica falhas internas do servidor ou exceções não tratadas no código Python.

### Limites e Ações de Alerta:

*   **Alerta de Carga de CPU (Médio):**
    *   *Gatilho:* Uso de CPU $> 80\%$ por mais de 5 minutos consecutivos.
    *   *Ação:* Disparo de notificação para o time de engenharia via e-mail/Slack.
*   **Alerta de Esgotamento de Memória (Crítico):**
    *   *Gatilho:* Consumo de RAM $> 90\%$.
    *   *Ação:* Comando automatizado de reinicialização do container Docker (`docker restart`) para limpar sessões inativas e evitar travamento do servidor.
*   **Alerta de Latência de Inferência (SLA):**
    *   *Gatilho:* Tempo médio de inferência $> 3.000\text{ ms}$ ($3\text{ s}$) em 10 requisições seguidas.
    *   *Ação:* Indicação de fila de requisições congestionada. Sugere a necessidade de escalonamento vertical (migrar de t2.micro para t3.medium) ou horizontal (adicionar réplicas por trás de um Load Balancer).

---



