#!/usr/bin/env python

from config import Schedule

class At(Schedule.RunPolicy):
    def __init__(self, time):
        self._time = time

    def schedule_for_daemon(self):
        return 'at %i' % self._time
    
def at(time):
    return At(time)

class ShellCommand(Schedule.Command):
    def __init__(self, command, resources):
        self._command = command
        self._resources = resources
        self._binary = command.split()[0]
        self._resources = resources

    def accept_transformation(self, transformation):
        self._command = transformation(self._command)

    def command(self):
        return self._command

    def sanity_checks(self):
        return ["which '%s'" % self._binary]

    def needed_resources(self):
        return self._resources

def shell(command, use_resources=[]):
    return ShellCommand(command, use_resources)

