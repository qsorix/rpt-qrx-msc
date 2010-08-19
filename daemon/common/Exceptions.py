#!/usr/bin/env python
# coding=utf-8

class DaemonError(Exception):
    def __init__(self, exception):
        Exception.__init__(self, exception)

class CommandError(Exception):
    def __init__(self, exception, cmd_id):
        self.cmd_id = cmd_id
        Exception.__init__(self, exception)

class ResolvError(DaemonError):
    pass

class LineError(DaemonError):
    pass

class ParentError(DaemonError):
    pass

class TypeError(DaemonError):
    pass

class ParamError(DaemonError):
    pass

class ValueError(DaemonError):
    pass

class DatabaseError(DaemonError):
    pass

class SchedulerError(DaemonError):
    pass
