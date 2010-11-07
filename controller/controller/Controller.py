#!/usr/bin/env python
# coding=utf-8

import datetime
import time

from ConnectionPlugin import ConnectionPlugin
from FrontendPlugin import FrontendPlugin
from common import Exceptions
from common import Database

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

        self._create_frontends(configured_test)
        self._test = configured_test

        try:
            self._send_configuration()
            sanity_exception = self._perform_sanity_check()

            if sanity_exception is None:
                self._perform_test()

            self._fetch_results()

            if sanity_exception:
                raise sanity_exception

        except Exception as e:
            print 'Aborting test because of exception: ' + str(e)
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
            self._frontends[name] = self._frontend_class(host)(host, connection, configured_test)

    def _send_configuration(self):
        for frontend in self._frontends.values():
            frontend.deploy_configuration()

    def _perform_sanity_check(self):
        try:
            for frontend in self._frontends.values():
                frontend.start_sanity_check()

            for frontend in self._frontends.values():
                # throws an exception in case of a problem
                frontend.wait_sanity_check()

            return None

        except Exceptions.SanityError as error:
            return error

    def _test_duration_policy(self):
        # calculate exact start moment
        setup_delay = datetime.timedelta(seconds=self._test.setup_phase_delay)
        now = datetime.datetime.now()
        start = now+setup_delay

        return TestDurationPolicy(start, self._test.end_policy)

    def _perform_test(self):
        # configuration is sane, start the test

        # instruct fronteds to start the test
        duration_policy = self._test_duration_policy()

        for frontend in self._frontends.values():
            frontend.start_test(duration_policy)

        self._monitor_running_frontends()

    def _monitor_running_frontends(self):
        running_frontends = self._frontends.values()
        remaining_triggers = set(self._test.triggers.values())

        # wait for the test to end
        while(running_frontends):
            # TODO instead of sleep, it should gather all open connections and
            # do a select()-like wait on them
            time.sleep(0.1)

            # iterate over running frontends and remove those which has
            # finished
            running_frontends = [f for f in running_frontends if not f.check_test_end()]

            activated_triggers = set([t for t in remaining_triggers if t.ready()])

            for trigger in activated_triggers:
                for frontend in running_frontends:
                    frontend.trigger(trigger['name'])

            remaining_triggers -= activated_triggers

    def _fetch_results(self):
        for frontend in self._frontends.values():
            frontend.fetch_results()
            Database.commit();


    def _abort_test(self):
        for frontend in self._frontends.values():
            frontend.abort_test()

