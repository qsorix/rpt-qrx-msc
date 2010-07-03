#!/usr/bin/evn python

from BaseMixins import NamedMixin

class Schedule:
    def __init__(self):
        self.__schedules = {}

    def host_schedule(self, host_name):
        return self.__schedules.setdefault(host_name, HostSchedule())

class HostSchedule(list):
    def schedule(self, name, run_policy, command):
        self.append(Event(name, run_policy, command))
        return self

class Event(NamedMixin):
    def __init__(self, name, run_policy, command):
        self.rename(name)
        self.__run_policy = run_policy
        self.__command = command

    def run_policy(self):
        return self.__run_policy

    def command(self):
        return self.__command

schedule = Schedule()
on = schedule.host_schedule

public_functions = {
        'on': on
    }
