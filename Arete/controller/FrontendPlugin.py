#!/usr/bin/env python
# coding=utf-8

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
    check_test_end
      nonblocking call. returns true if the test has finished
      can receive trigger notifications
    fetch_results
    abort_test
    trigger(name) - send trigger event to slave
    ====================
    """

    needed_attributes = []

    __metaclass__ = PluginMount

    @staticmethod
    def lookup(name):
        for p in FrontendPlugin.plugins:
            if p.frontend_type == name:
                return p

        raise RuntimeError("Frontend plugin for type '%s' was not registered" % name)

    def __init__(self, host, connection_class, configured_test, **kwargs):
        self._host = host
        self._configured_test = configured_test
        self._connection_class = connection_class
        self._connection = connection_class(self.host())

    def configuration(self):
        return self._configured_test

    def connection(self):
        return self._connection

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

    def start_test(self, duration_policy):
        pass

    def wait_test(self):
        pass

    def fetch_results(self):
        pass

    def abort_test(self):
        pass

 