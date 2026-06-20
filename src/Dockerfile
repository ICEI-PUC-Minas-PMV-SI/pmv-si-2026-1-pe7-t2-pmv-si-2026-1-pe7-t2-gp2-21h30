# Usar imagem base leve oficial do Python
FROM python:3.10-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Instalar dependências básicas do sistema necessárias para compilação e healthcheck
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar primeiro apenas o requirements.txt para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código-fonte do diretório src/ para o container
COPY . .

# Expor a porta padrão do Streamlit
EXPOSE 8501

# Adicionar um Healthcheck para monitorar a saúde do container na nuvem
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para iniciar a aplicação streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
