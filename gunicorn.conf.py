import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 1  # Render Free Tier: apenas 1 worker
worker_class = "sync"

# Evita encerramento precoce de requisições longas (ex: IA)
timeout = 120
graceful_timeout = 30
worker_timeout = 120

# Configuração leve para manter conexões
keepalive = 2
max_requests = 500
max_requests_jitter = 50

# Log para terminal Render
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Pré-carrega app para melhorar performance
preload_app = True
