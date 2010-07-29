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
        FIXME: describe them better
    ====================
    start_sanity_check
    wait_sanity_check
    deploy_configuration
    start_test
    wait_test
    fetch_results
    abort_test
    ====================
    """

    needed_attributes = []

    __metaclass__ = PluginMount

    def __init__(self, host, connection_class, **kwargs):
        self._host = host
        self._connection_class = connection_class
        self._connection = connection_class(self.host())

    def output(self):
        assert self._connection
        return self._connection.output()

    def input(self):
        assert self._connection
        return self._connection.input()

    def connect(self):
        self._connection.connect()

    def disconnect(self):
        if self._connection:
            self._connection.close()

    def host(self):
        return self._host

    # FIXME: remove these, it is not pythonish
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

    def abort_test(self):
        pass

 
