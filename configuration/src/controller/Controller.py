#!/usr/bin/env python

import sys
from ConnectionPlugin import ConnectionPlugin
from FrontendPlugin import FrontendPlugin

#FIXME: loads the module so the plugin in it can register itself.
#       rather than doing this, write some logic in Main.py to find and load
#       plugin modules
import DaemonFrontend

class DummyConnection(ConnectionPlugin):
    connection_type = 'tcp'

    def __init__(self, host):
        self._host = host
        self._name = host.model.name()
        print self._name+'> ', ' -- connected --'

    def input(self):
        class DummyLine:
            def readline(s):
                ans = '200 OK'
                #print self._name+'< ', ans
                return ans

        return DummyLine()

    def output(self):
        class decorator:
            def write(s, str):
                print self._name+'> ', str,

        return decorator()

    def close(self):
        print self._name+'> ', ' -- disconnected --'

class Controller:
    def run(self, configured_test):
        self._create_frontends(configured_test)

        try:
            self._send_configuration()
            self._perform_sanity_check()
            self._perform_test()
            self._fetch_results()

        # FIXME:
        except:
            raise

    def _connection(self, host):
        """
        Find out how and connect to given host.

        Return connection object allowing streamed IO.
        """
        driver_name = host.network.attributes()['connection']

        for plugin in ConnectionPlugin.plugins:
            if plugin.connection_type == driver_name:
                return plugin

        raise RuntimeError("Connection plugin for type '%s' was not registered" % driver_name)

    def _frontend_class(self, host):
        frontend = host.network.attributes()['frontend']

        for plugin in FrontendPlugin.plugins:
            if plugin.frontend_type == frontend:
                return plugin

        raise RuntimeError("Frontend plugin for type '%s' was not registered" % frontend)

    def _create_frontends(self, configured_test):
        self._frontends = {}
        for (name, host) in configured_test.hosts.items():
            connection = self._connection(host)
            self._frontends[name] = self._frontend_class(host)(host, connection)

    def _send_configuration(self):
        for frontend in self._frontends.values():
            frontend.deploy_configuration()

    def _perform_sanity_check(self):
        # TODO: perform synchronization. as part of environment&sanity check or on its own

        for frontend in self._frontends.values():
            frontend.start_sanity_check()

        # now, if sanity check failed on any host, we can/must abort the test
        for frontend in self._frontends.values():
            frontend.wait_sanity_check()

    def _perform_test(self):
        # configuration is sane, start the test
        start_time = '<FIXME timestamp>'
        for frontend in self._frontends.values():
            frontend.start_test(start_time)

        # wait for the test to end
        for frontend in self._frontends.values():
            frontend.wait_test()

    def _fetch_results(self):
        for frontend in self._frontends.values():
            frontend.fetch_results()
