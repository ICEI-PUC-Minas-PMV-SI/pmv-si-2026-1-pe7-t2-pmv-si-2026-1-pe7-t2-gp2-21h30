# Análise da Variabilidade Regional do Mercado Automotivo Brasileiro via RENAVAM

`CURSO: Sistemas de Informação`

`DISCIPLINA: Projeto - Pesquisa e Experimentação em Sistemas de Informação`

`SEMESTRE: 7º`

Este projeto surge no contexto da disciplina de Projeto: Pesquisa e Experimentação em Sistemas de Informação (7º Período). A investigação foca na análise do **Registro Nacional de Veículos Automotores (RENAVAM)** para demonstrar como o mercado automotivo brasileiro é moldado por fatores regionais. O objetivo é utilizar Ciência de Dados e Aprendizado de Máquina para mapear como clima, cultura local, infraestrutura e perfil socioeconômico influenciam a frota de cada município. O público-alvo compreende gestores do setor automotivo, planejadores urbanos e analistas de mercado que buscam transformar dados públicos em decisões estratégicas.

## Integrantes

* André Ramos
* Gilberto modesto
* Gustavo Gino Pereira
* Isabella Carolina de Almeida Siqueira Damião
* Natã Gabriel Teixeira
* Rhafael Hector de Siqueira Damião
* Thiago Ferreira de Oliveira

## Orientador

* Neil Paiva Tizzo

# Planejamento

| Etapa         | Atividades |
|  :----:   | ----------- |
| ETAPA 1         |[Documentação de Contexto e levantamento dos dados](docs/contexto.md) <br> |
| ETAPA 2         |[Conhecendo os dados](docs/conhecendo-dados.md) <br> |
| ETAPA 3         |[Preparação dos dados, construção e avaliação do modelo proposto](docs/construindo-modelo.md) |
| ETAPA 4         |[Preparação dos dados, construção, avaliação e comparação dos modelos propostos](docs/construindo-modelos.md) |
| ETAPA 5         |[Implantação e apresentação da solução](docs/implantação-apresentacao.md) <br>  |

## Instruções de utilização

### 🌐 Acesso em Produção (Deploy em Nuvem)
* **URL Pública:** [https://frota-diesel-eixo7.onrender.com](https://frota-diesel-eixo7.onrender.com)
* **Status:** Online / Produção

---

### 💻 Execução Local da Aplicação Web

Para executar o painel de inferência dinâmica localmente em sua máquina, siga os passos abaixo:

#### Pré-requisitos:
- Python 3.10 ou superior instalado.

#### Passos para Execução:
1. Navegue até a pasta raiz do repositório.
2. Instale as dependências requeridas utilizando o `pip`:
   ```bash
   pip install -r src/requirements.txt
   ```
3. Execute o servidor do Streamlit apontando para o arquivo da aplicação:
   ```bash
   streamlit run src/app.py
   ```
4. O seu navegador abrirá automaticamente no endereço: `http://localhost:8501`.

---

### 🐳 Execução via Docker (Container)

Se preferir rodar a solução de forma isolada em um container compatível com qualquer nuvem:

1. Certifique-se de ter o **Docker** instalado e ativo em sua máquina.
2. Realize o build da imagem Docker utilizando a pasta `src/` como contexto:
   ```bash
   docker build -t frota-diesel-app -f src/Dockerfile src/
   ```
3. Execute o container mapeando a porta padrão `8501`:
   ```bash
   docker run -d -p 8501:8501 --name painel-frota frota-diesel-app
   ```
4. Acesse em seu navegador: `http://localhost:8501`.

# Código

<li><a href="src/README.md"> Código Fonte</a></li>

# Apresentação

<li><a href="presentation/README.md"> Apresentação da solução</a></li>
