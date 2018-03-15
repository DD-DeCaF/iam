import multiprocessing
import os


_environment = os.environ['ENVIRONMENT']

bind = "0.0.0.0:8000"
worker_class = "gevent"
timeout = 20
loglevel = "info"
accesslog = "-"

if _environment == 'production':
    workers = multiprocessing.cpu_count() * 2 + 1
    preload_app = True
    access_log_format = """"%(r)s" %(s)s %(b)s %(L)s "%(f)s\""""
else:
    workers = 1
    reload = True
    access_log_format = """%(t)s "%(r)s" %(s)s %(b)s %(L)s "%(f)s\""""
