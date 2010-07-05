#!/usr/bin/env python

import sys

class Frontend:
    """
    Base class for frontend implementation.
    """
    def __init__(self, host, connection):
        self._connection = connection
        self._host = host

    def connection(self):
        return self._connection

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

class DaemonFrontend(Frontend):
    def deploy_configuration(self):
        host_commands = self.host().commands
        resources = self.host().resources

        for r in resources:
            r.transfer_with_daemon(self)

        self._send_command("check %i:\n" % len(host_commands.check()))
        for c in host_commands.check():
            self._send_command(c + '\n')

        self._send_command("setup %i:\n" % len(host_commands.setup()))
        for c in host_commands.setup():
            self._send_command(c + '\n')

        self._send_command("schedule %i:\n" % len(host_commands.schedule()))
        for c in host_commands.schedule():
            self._send_command(c + '\n')

        self._send_command("cleanup: %i\n" % len(host_commands.cleanup()))
        for c in host_commands.cleanup():
            self._send_command(c + '\n')

    def start_test(self, timestamp):
        self._send_command('start at: ' + timestamp + '\n')

    def _send_command(self, cmd):
        self.connection().output().write(cmd)
        resp = self.connection().input().readline()

        if resp.split()[0] != '200':
            raise RuntimeError('Frontned got wrong response')

class DummyConnection:
    def __init__(self, name):
        self._name = name

    def input(self):
        class DummyLine:
            def readline(self):
                return '200 OK'

        return DummyLine()

    def output(self):
        return sys.stdout

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
        return DummyConnection(host)

    def _frontend_class(self, host):
        return DaemonFrontend

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
