#!/usr/bin/evn python

from BaseMixins import NamedMixin

class Command:
    """
    Base class for commands.

    Allows users to store commands and generate sanity checks they need.

    Provides methods:
        def command(self):

            Returns a string representing the command to execute.

        def accept_transformation(self, transformation_function):

            Apply transformation_function to the stored command and store the
            result instead.

            This is used to perform variables substitution in command strings.
    """

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

class Schedule(NamedMixin):
    def __init__(self, name):
        self.rename(name)
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

_schedule = None

def create_schedule(name):
    global _schedule
    if _schedule:
        raise Exceptions.ConfigurationError('You cannot create more than one schedule.')
    _schedule = Schedule(name)

def get_schedule():
    global _schedule
    return _schedule

def append_schedule(*args, **kwargs):
    s = get_schedule()
    if not s:
        raise Exceptions.ConfigurationError('These is no schedule. Did you forget to call \'create_schedule(name)\' before calling append_schedule?')

    return s.append_schedule(*args, **kwargs)

public_functions = {
    'create_schedule': create_schedule,
    'get_schedule': get_schedule,
    'append_schedule': append_schedule
}
