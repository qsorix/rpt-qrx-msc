from common.PluginMount import PluginMount

class FrontendPlugin:
    """
    Mount point for plugins which implement frontends

    Plugins implementing this reference should provide the following attributes:

    =================  =======================================================
    frontend_type      String naming frontend type for this plugin. This will
                       be matched agains network host's frontend attribute.

    needed_attributes  List of attributes that must be set for a device if
                       this frontend is to be used. Will revoke configurations
                       without those attributes set.
                       Defaults to [].
    =================  =======================================================

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

    needed_attributes = []

    __metaclass__ = PluginMount

    def __init__(self, host, connection_class, **kwargs):
        self._connection_class = connection_class
        self._connection = None
        self._host = host

    def output(self):
        assert self._connection
        return self._connection.output()

    def input(self):
        assert self._connection
        return self._connection.input()

    def connect(self):
        assert not self._connection
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

 
