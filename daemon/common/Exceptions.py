#!/usr/bin/env python
# coding=utf-8

class DaemonError(Exception):
    def __init__(self, exception):
        Exception.__init__(self, exception)

class CheckError(DaemonError):
    pass

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

class DatabaseError(Exception):
    pass

