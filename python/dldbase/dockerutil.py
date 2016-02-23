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
        except Exception as e:
            raise RuntimeError("Encountered problem when interacting with your Docker Engine:\n"
                               "{err_repr}\n"
                               " * Is the Docker Daemon up and running?\n"
                               " * Does the daemon use TLS? (currently unsupported by this tool)".format(
                    err_repr=repr(e)))
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.client.close()
        except Exception as ex:
            DOCKER_CLIENT_LOG.debug("exception when closing {s} for cleanup:\n{e}".format(s=self, e=ex))

def docker_client(*args, **kwargs):
    return DockerClientContext(*args, **kwargs)
