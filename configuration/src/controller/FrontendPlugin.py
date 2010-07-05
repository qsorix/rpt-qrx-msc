from common.PluginMount import PluginMount

class FrontendPlugin:
    """
    Mount point for plugins which implement frontends

    Plugins implementing this reference should provide the following attributes:

    =============  ==========================================================
    frontend_type  String naming frontend type for this plugin. This will be
                   matched agains network host's frontend attribute.
    =============  ==========================================================

    and reimplement methods:
    ====================
    start_sanity_check
    wait_sanity_check
    deploy_configuration
    start_test
    wait_test
    fetch_results
    ====================
    """

    __metaclass__ = PluginMount

    def __init__(self, host, connection_class):
        self._connection_class = connection_class
        self._connection = None
        self._host = host

    def connection(self):
        return self._connection

    def connect(self):
        self._connection = self._connection_class(self.host())

    def disconnect(self):
        if self._connection:
            self._connection.close()
        self._connection = None

    def host(self):
        return self._host

    def start_sanity_check(self):
        pass

    def wait_sanity_check(self):
        pass

    def deploy_configuration(self, host_configuration):
        pass

    def start_test(self, timestamp):
        pass

    def wait_test(self):
        pass

    def fetch_results(self):
        pass

 
