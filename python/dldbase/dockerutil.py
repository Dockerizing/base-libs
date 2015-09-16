# Python2/3 compatibility layer - write Python 3-like code executable by a Python 2.7. runtime
from __future__ import absolute_import, division, print_function, unicode_literals
from future.standard_library import install_aliases

install_aliases()
from builtins import *

import logging
import docker
from requests.exceptions import ConnectionError

DOCKER_CLIENT_LOG = logging.getLogger('dld.dockerclient')

class DockerClientContext(object):

    def __init__(self, *args, **kwargs):
        self.client_args = args
        self.client_kwargs = kwargs

    def __enter__(self):
        self.client = docker.Client(*self.client_args, **self.client_kwargs)
        try:
            self.client.version()
        except ConnectionError as ce:
            raise RuntimeError("Encountered problem when interacting with your Docker Engine:\n"
                               "{e.__class__.__name__}: {e.message}\n"
                               " * Is the Docker Daemon up and running?\n"
                               " * Does the daemon use TLS? (currently unsupported by this tool)".format(e=ce))
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.client.close()
        except Exception as ex:
            DOCKER_CLIENT_LOG.debug("exception when closing {s} for cleanup:\n{e}".format(s=self, e=ex))

def docker_client(*args, **kwargs):
    return DockerClientContext(*args, **kwargs)
