# Gunicorn configuration file for Azure production deployment
import multiprocessing

# Recommended worker count is (2 x NUM_CORES) + 1
workers = multiprocessing.cpu_count() * 2 + 1
bind = "0.0.0.0:8000"
timeout = 120
accesslog = "-"  # log to stdout for Azure to capture
errorlog = "-"   # log to stderr for Azure to capture
loglevel = "info"
