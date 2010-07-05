#!/usr/bin/evn python

from BaseMixins import NamedMixin

class RunPolicy:
    """Base class for run policies.

    Implement schedule_for_<frontend> in your subclasses."""

    pass

class Schedule:
    def __init__(self):
        self._schedules = {}

    def host_schedule(self, host_name):
        return self._schedules.setdefault(host_name, HostSchedule())

class HostSchedule(list):
    def schedule(self, name, run_policy, command):
        self.append(Event(name, run_policy, command))
        return self

class Event(NamedMixin):
    def __init__(self, name, run_policy, command):
        self.rename(name)
        self._run_policy = run_policy
        self._command = command

    def run_policy(self):
        return self._run_policy

    def command(self):
        return self._command

schedule = Schedule()
on = schedule.host_schedule

public_functions = {
        'on': on
    }
