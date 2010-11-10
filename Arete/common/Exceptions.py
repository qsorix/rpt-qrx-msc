#!/usr/bin/env python
# coding=utf-8

class ConfigurationError(Exception):
    def __init__(self, exception, traceback=None):
        Exception.__init__(self, exception)
        self.traceback = traceback

class SanityError(ConfigurationError):
    pass

class NotBoundError(ConfigurationError):
    pass

class NameExistsError(ConfigurationError):
    pass

class MissingPluginError(ConfigurationError):
    pass

class SlaveError(Exception):
    def __init__(self, exception, traceback=None):
        Exception.__init__(self, exception)
        self.traceback = traceback
