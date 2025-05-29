# Use Python 3.11 slim como base para menor tamanho
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=3000

# Criar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para otimizar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expor a porta que o Coolify espera
EXPOSE 3000

# Comando para iniciar a aplicação com Gunicorn usando arquivo de configuração
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"] 
