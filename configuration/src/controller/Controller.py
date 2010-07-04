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

    def start_test(self, timestamp):
        pass

    def fetch_results(self):
        pass

class DaemonFrontend(Frontend):
    def deploy_configuration(self, host_commands, resources=[]):
        for r in resources:
            r.transfer_with_daemon(self)

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

        frontends = {}

        for (name, host) in configured_test.hosts.items():
            connection = self._connect(host)
            frontends[name] = self._frontend_class(host)(connection)

            r = [configured_test.resources[rname] for rname in host.resources]
            frontends[name].deploy_configuration(prepared_commands[name], resources=r)

        #for frontend in frontends.values():
            #frontend.start_sanity_check()

        # now, if sanity check failed on any host, we can/must abort the test

        #for frontend in frontends.values():
            #frontend.wait_sanity_check()

        # otherwise start it
        for frontend in frontends.values():
            frontend.start_test('<FIXME timestamp>')

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
