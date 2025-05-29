import os

# Configuração do servidor
bind = f"0.0.0.0:{os.environ.get('PORT', '3000')}"
workers = 1
threads = 2
timeout = 120
keepalive = 2

# Configuração de logs
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configuração do processo
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# Configuração de segurança
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190 