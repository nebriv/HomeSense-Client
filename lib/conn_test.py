import logging

logger = logging.getLogger(__name__)


def test_network_connection():
    import socket
    REMOTE_SERVER = "www.google.com"
    logger.debug("Checking network connection")

    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        pass
    return False