#!/usr/bin/env python
# coding=utf-8

import uuid
import datetime
import time

from ConnectionPlugin import ConnectionPlugin
from FrontendPlugin import FrontendPlugin
from common import Exceptions
from controller import Database

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
        self._test = configured_test

        try:
            self._send_configuration()
            self._perform_sanity_check()

            # FIXME: at this point frontends must be synchronized with slaves.

            self._perform_test()

            self._fetch_results()

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
            self._frontends[name] = self._frontend_class(host)(host, connection, test_uuid=self._test_uuid, triggers=configured_test.triggers)

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

        self._start_time = datetime.datetime.now()

        configured_test = self._test

        # calculate exact start moment
        setup_delay = datetime.timedelta(seconds=configured_test.setup_phase_delay)
        now = datetime.datetime.now()
        start = now+setup_delay

        duration_policy = TestDurationPolicy(start, configured_test.end_policy)

        # instruct fronteds to start the test
        for frontend in self._frontends.values():
            frontend.start_test(duration_policy)

        # store here fired triggers
        # so we don't fire the same trigger twice
        notified_triggers = set()

        # wait for the test to end
        all_finished = False
        while(not all_finished):
            time.sleep(1.0)
            all_finished = True
            for frontend in self._frontends.values():
                finished = frontend.check_test_end()
                all_finished = all_finished and finished

            for trigger in configured_test.triggers.values():
                if trigger.ready() and trigger['name'] not in notified_triggers:
                    for frontend in self._frontends.values():
                        frontend.trigger(trigger['name'])

                    notified_triggers.add(trigger['name'])

        self._duration = datetime.datetime.now() - self._start_time

    def _fetch_results(self):
        Database.Test(id=unicode(self._test_uuid), start_time=self._start_time, duration=self._duration)
        Database.commit();

        for frontend in self._frontends.values():
            frontend.fetch_results()
            Database.commit();


    def _abort_test(self):
        for frontend in self._frontends.values():
            frontend.abort_test()

