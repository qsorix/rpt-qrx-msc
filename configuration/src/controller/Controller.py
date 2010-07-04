#!/usr/bin/env python

import sys

class Frontend:
    """
    Base class for frontend implementation.
    """
    def __init__(self, connection):
        self.__connection = connection

    def connection(self):
        return self.__connection

    def deploy_configuration(self, host):
        pass

    def fetch_results(self):
        pass

class DaemonFrontend(Frontend):
    def deploy_configuration(self, host):
        self._send_command('foo\n')

    def _send_command(self, cmd):
        self.connection().output().write(cmd)
        resp = self.connection().input().readline()

        print resp

        if resp.split()[0] != '200':
            raise RuntimeError('Frontned got wrong response')

class DummyConnection:
    def __init__(self, name):
        self.__name = name

    def input(self):
        class DummyLine:
            def readline(self):
                return '200 OK'

        return DummyLine()

    def output(self):
        return sys.stdout

class Controller:
    def __init__(self):
        self.__frontends = {}

    def run(self, configured_test, prepared_commands):
        print configured_test.resources

        frontends = {}

        for (name, host) in configured_test.hosts.items():
            connection = self._connect(host)
            frontends[name] = self._frontend_class(host)(connection)

            frontends[name].deploy_configuration(prepared_commands[name])

        #for frontend in frontends.values():
        #    frontend.

        # FIXME: from the schedule it must be possible to deduce the test's
        # duration
        #wait_for_all_tasks

        for host in configured_test.hosts:
            frontends[host].fetch_results()

    def _connect(self, host):
        """
        Find out how and connect to given host.

        Return connection object allowing streamed IO.
        """
        return DummyConnection(host.model.name())

    def _frontend_class(self, host):
        return DaemonFrontend
