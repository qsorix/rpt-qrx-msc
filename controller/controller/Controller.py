#!/usr/bin/env python

import sys
import uuid
import datetime

from ConnectionPlugin import ConnectionPlugin
from FrontendPlugin import FrontendPlugin
from common import Exceptions

class TestDurationPolicy:
    def __init__(self, start, end_policy):
        """
        Start is datetime.datetime instance

        end_policy is passed from configuration
        """
        self._start = start
        self._end_policy = end_policy

    def start(self):
        """
        When to start the test

        This returns local time, frontends must add the time offset
        acquired during synchronization phase.
        """
        return self._start

    def end_policy(self):
        """
        How should the test end?

        Returns one of two strings:
          'duration <seconds>' where <seconds> is a value convertible to float.
            This tells that the test will end at <seconds> after start().

          'complete'
            This tells frontends must wait to receive notification from slave,
            informing that all scheduled tasks were completed (including
            cleanup).
        """
        return self._end_policy

class Controller:
    def run(self, configured_test):

        self._test_uuid = uuid.uuid4()
        self._create_frontends(configured_test)

        try:
            self._send_configuration()
            self._perform_sanity_check()

            # FIXME: at this point frontends must be synchronized with slaves.

            self._perform_test(configured_test)
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

    def _perform_test(self, configured_test):
        # configuration is sane, start the test

        # calculate exact start moment
        setup_delay = datetime.timedelta(seconds=configured_test.setup_phase_delay)
        now = datetime.datetime.now()
        start = now+setup_delay

        duration_policy = TestDurationPolicy(start, configured_test.end_policy)

        # instruct fronteds to start the test
        for frontend in self._frontends.values():
            frontend.start_test(duration_policy)

        # FIXME: during the test we have to read/write some stuff, like
        # notification about finished tests, or triggers if they're going to be
        # implemented
        # this is a place to do it. think about some collective algorithm that
        # won't break encapsulation and will work with all frontends in
        # "parallel".

        # wait for the test to end
        for frontend in self._frontends.values():
            frontend.wait_test()

    def _fetch_results(self):
        for frontend in self._frontends.values():
            frontend.fetch_results()

    def _abort_test(self):
        for frontend in self._frontends.values():
            frontend.abort_test()

