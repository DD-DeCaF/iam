import multiprocessing
import os


_configuration = os.environ['CONFIGURATION']

bind = "0.0.0.0:8000"
worker_class = "gevent"
timeout = 30
loglevel = "info"
accesslog = "-"
access_log_format = """%(t)s "%(r)s" %(s)s %(b)s %(L)s "%(f)s\""""

if _configuration == 'prod':
    workers = multiprocessing.cpu_count() * 2 + 1
    preload_app = True
else:
    workers = 1
    reload = True
