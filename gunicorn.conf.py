import multiprocessing
import os

# Binding
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")

# Worker Options
workers = 1
threads = 4
worker_class = "gthread"
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
