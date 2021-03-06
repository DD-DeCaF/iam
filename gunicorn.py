# Copyright (c) 2018, Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Configure the gunicorn server."""

import os
import warnings

import gevent.monkey
from prometheus_client import multiprocess


# Ensure gevent is monkeypatched before ssl is imported (gunicorn does this too
# late). Note that this is only necessary when `preload_app` is True, and the
# fact that the following warning *will* be printed
# See also https://github.com/gevent/gevent/issues/1016 and
# https://github.com/benoitc/gunicorn/issues/1566
with warnings.catch_warnings():
    # Ignore the monkey-patch warning; recursion errors do not occur (eg. on use
    # of `requests` when the monkey-patch occurs here.
    warnings.simplefilter("ignore")
    gevent.monkey.patch_all()

_config = os.environ["ENVIRONMENT"]

bind = "0.0.0.0:8000"
worker_class = "gevent"
timeout = 20
accesslog = "-"
access_log_format = '''%(t)s "%(r)s" %(s)s %(b)s %(L)s "%(f)s"'''


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)


if _config in ["production", "staging"]:
    # Our resource policy is that each web service is granted at least a single
    # vCPU when available. The number of workers is then a guess that having two
    # workers I/O bound and a third processing a request will utilize available
    # resources well, but that guess needs to be tested and benchmarked.
    workers = 3
    preload_app = True
else:
    workers = 1
    reload = True
