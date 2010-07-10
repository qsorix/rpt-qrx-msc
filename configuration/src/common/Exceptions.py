#!/usr/bin/env python

class ConfigurationError(Exception):
    def __init__(self, exception, traceback=None):
        Exception.__init__(self, exception)
        self.traceback = traceback

class SanityError(ConfigurationError):
    pass

class NotBoundError(Exception):
    pass

class NameExistsError(Exception):
    pass

class MissingPluginError(Exception):
    pass
