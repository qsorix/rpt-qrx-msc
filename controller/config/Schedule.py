#!/usr/bin/evn python

from BaseMixins import NamedMixin

from Utils import resolve_host_name

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
        self._test_end_policy = None
        self._setup_phase_delay = 1.0 # 1 second default

    def set_test_end_policy(self, test_end_policy):
        self._test_end_policy = test_end_policy

    def test_end_policy(self):
        return self._test_end_policy

    def set_setup_phase_delay(self, setup_phase_delay):
        self._setup_phase_delay = setup_phase_delay

    def setup_phase_delay(self):
        return self._setup_phase_delay

    def host_schedule(self, host):
        if isinstance(host, str):
            host = resolve_host_name(host)

        return self._schedules.setdefault(host['name'], HostSchedule())

    def append_schedule(self, host, schedule):
        if isinstance(host, str):
            host = resolve_host_name(host)

        host_schedule = self.host_schedule(host['name'])

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

def get_schedule(validate=True):
    global _schedule
    if validate and _schedule is None:
        raise Exceptions.ConfigurationError('These is no schedule. Did you forget to call \'create_schedule(name)\'?')
    return _schedule

def append_schedule(*args, **kwargs):
    return get_schedule().append_schedule(*args, **kwargs)

def test_end_policy(end_policy, setup_phase_delay = None):
    get_schedule().set_test_end_policy(end_policy)
    if setup_phase_delay:
        get_schedule().set_setup_phase_delay(setup_phase_delay)

public_functions = {
    'create_schedule': create_schedule,
    'get_schedule': get_schedule,
    'append_schedule': append_schedule,
    'test_end_policy': test_end_policy
}
