#!/usr/bin/env python

from config import Schedule

class At(Schedule.RunPolicy):
    def __init__(self, time):
        self.__time = time

    def schedule_for_daemon(self):
        return 'at %i' % self.__time
    
def at(time):
    return At(time)

