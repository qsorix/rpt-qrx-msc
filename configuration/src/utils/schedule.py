#!/usr/bin/env python

from config import Schedule

class At(Schedule.RunPolicy):
    def __init__(self, time):
        self._time = time

    def schedule_for_daemon(self):
        return 'at %i' % self._time
    
def at(time):
    return At(time)

