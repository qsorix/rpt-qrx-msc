#!/usr/bin/env python

from config import Schedule

class at(Schedule.RunPolicy):
    def __init__(self, time):
        self._time = time

    def schedule_for_daemon(self):
        return 'in %i' % self._time

class every(Schedule.RunPolicy):
    def __init__(self, time):
        self._time = time

    def schedule_for_daemon(self):
        return 'every %i' % self._time

class after(Schedule.RunPolicy):
    def __init__(self, cmd):
        self._cmd = cmd

    def schedule_for_daemon(self):
        return 'after %s' % self._cmd
    
class shell(Schedule.Command):
    def __init__(self, command, use_resources=[]):
        self._command = command
        self._binary = command.split()[0]
        self._resources = use_resources

    def accept_transformation(self, transformation):
        self._command = transformation(self._command)

    def command(self):
        return self._command

    def sanity_checks(self):
        return ["which '%s'" % self._binary]

    def needed_resources(self):
        return self._resources

class ClientServer:
    def __init__(self, name, server_command, client_command):
        self._sname = name+'_server'
        self._cname = name+'_client'
        self._scmd = server_command
        self._ccmd = client_command

    def server(self, start, end):
        start_policy = at(start)
        end_policy = at(end)
        return [
            (self._sname, start_policy, shell(self._scmd)),
            (self._sname+'_kill', end_policy, shell('kill @{%s.pid}' % self._sname))
        ]

    def client(self, start, end, server):
        start_policy = at(start)
        end_policy = at(end)

        ccmd = self._ccmd.replace('@{server', '@{%s' % server)

        return [
            (self._cname, start_policy, shell(ccmd)),
            (self._cname+'_kill', end_policy, shell('kill @{%s.pid}' % self._cname))
        ]

