#!/usr/bin/env python

import sys
import uuid

from ConnectionPlugin import ConnectionPlugin
from FrontendPlugin import FrontendPlugin
from common import Exceptions

class Controller:
    def run(self, configured_test):

        self._test_uuid = uuid.uuid4()
        self._create_frontends(configured_test)

        try:
            self._send_configuration()
            self._perform_sanity_check()
            self._perform_test()
            self._fetch_results()

        except:
            self._abort_test()
            raise

    def _connection_class(self, host):
        """
        Find out how and connect to given host.

        Return connection object allowing streamed IO.
        """
        driver_name = host.device['connection']

        plugin = ConnectionPlugin.lookup(driver_name)

        for attr in plugin.needed_attributes:
            if attr not in host.device.attributes():
                raise Exceptions.ConfigurationError("Connection plugin for type '%s' needs '%s' attribute to be set for a device." % (driver_name, attr))

        return plugin

    def _frontend_class(self, host):
        frontend = host.device['frontend']

        plugin = FrontendPlugin.lookup(frontend)

        for attr in plugin.needed_attributes:
            if attr not in host.device.attributes():
                raise Exceptions.ConfigurationError("Frontend plugin for type '%s' needs '%s' attribute to be set for a device." % (frontend, attr))

        return plugin

    def _create_frontends(self, configured_test):
        self._frontends = {}
        for (name, host) in configured_test.hosts.items():
            connection = self._connection_class(host)
            self._frontends[name] = self._frontend_class(host)(host, connection, test_uuid=self._test_uuid)

    def _send_configuration(self):
        for frontend in self._frontends.values():
            frontend.deploy_configuration()

    def _perform_sanity_check(self):
        # TODO: perform synchronization. as part of environment&sanity check or on its own

        for frontend in self._frontends.values():
            frontend.start_sanity_check()

        for frontend in self._frontends.values():
            # throws an exception in case of a problem
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

    def _abort_test(self):
        for frontend in self._frontends.values():
            frontend.abort_test()

