#!/usr/bin/evn python

from BaseMixins import NamedMixin

class Command:
    """
    Base class for commands.

    Allows users to store commands and generate sanity checks they need.

    Provides methods:
        command()       - returns command string
        sanity_checks() - returns a list of commands to execute during sanity
                          check phase

    """
    def command(self):
        """
        Returns a string representing the command to execute.
        """
        return None

    def sanity_checks(self):
        """
        Returns a list of commands to execute during sanity check phase.
        """
        return []

    def needed_resources(self):
        """
        Returns a list of resources needed for this command.
        """
        return []

class RunPolicy:
    """
    Base class for run policies.

    Implement schedule_for_<frontend> in your subclasses.
    """
    pass

class Schedule:
    def __init__(self):
        self._schedules = {}

    def host_schedule(self, host_name):
        return self._schedules.setdefault(host_name, HostSchedule())

    def append_schedule(self, host_name, schedule):
        host_schedule = self.host_schedule(host_name)

        for name, run_policy, command in schedule:
            e = Event(name, run_policy, command)
            host_schedule.append(e)

class HostSchedule(list):
    def schedule(self, name, run_policy, command):
        self.append(Event(name, run_policy, command))
        return self

class Event(NamedMixin):
    def __init__(self, name, run_policy, command):
        self.rename(name)
        self._run_policy = run_policy
        self._command = command

    def run_policy(self): return self._run_policy
    def command(self): return self._command

schedule = Schedule()
append_schedule = schedule.append_schedule

public_functions = {
        'append_schedule': append_schedule
    }
