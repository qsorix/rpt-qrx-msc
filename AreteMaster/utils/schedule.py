#!/usr/bin/env python
# coding=utf-8

from AreteMaster.config import Schedule

class at(Schedule.RunPolicy):
    def __init__(self, time):
        self._time = time

    def schedule_for_arete_slave(self):
        return 'at %i' % self._time

class every(Schedule.RunPolicy):
    def __init__(self, time):
        self._time = time

    def schedule_for_arete_slave(self):
        return 'every %i' % self._time

class after(Schedule.RunPolicy):
    def __init__(self, cmd):
        self._cmd = cmd

    def schedule_for_arete_slave(self):
        return 'after %s' % self._cmd

class trigger(Schedule.RunPolicy):
    def __init__(self, trigger):
        self._trigger = trigger

    def schedule_for_arete_slave(self):
        return 'trigger %s' % self._trigger

class poke(Schedule.RunPolicy):
    def __init__(self, poke):
        self._poke = poke

    def schedule_for_arete_slave(self):
        return 'poke %s' % self._poke
    
class shell(Schedule.Command):
    def __init__(self, command, use_resources=[], check_executable=True):
        self._command = command
        self._binary = command.split()[0]
        self._resources = use_resources
        self._check_executable = check_executable

    def command_type(self):
        return 'shell'

    def accept_transformation(self, transformation):
        self._command = transformation(self._command)

    def command(self):
        return self._command

    def sanity_checks(self):
        if self._check_executable:
            return ["which '%s'" % self._binary]
        else:
            return []

    def needed_resources(self):
        return self._resources

class notify(Schedule.Command):
    def __init__(self, trigger_name):
        self._trigger_name = trigger_name

    def command_type(self):
        return 'notify'

    def sanity_checks(self):
        return []

    def accept_transformation(self, transformation):
        self._trigger_name = transformation(self._trigger_name)

    def command(self):
        return self._trigger_name

class ClientServer:
    def __init__(self, name, server_command, client_command):
        self._sname = name+'_server'
        self._cname = name+'_client'
        self._scmd = server_command
        self._ccmd = client_command

    def server(self, start, end):
        start_policy = at(start)
        end_policy = at(end)
        result = [(self._sname, start_policy, shell(self._scmd))]
        if end is not None:
            result.append((self._sname+'_kill', end_policy, shell('kill @{%s.pid}' % self._sname)))

        return result

    def client(self, start, end, server):
        start_policy = at(start)
        end_policy = at(end)

        ccmd = self._ccmd.replace('@{server', '@{%s' % server)

        result = [(self._cname, start_policy, shell(ccmd))]
        if end is not None:
            result.append((self._cname+'_kill', end_policy, shell('kill @{%s.pid}' % self._cname)))

        return result

