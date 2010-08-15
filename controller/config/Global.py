#!/usr/bin/env python
import getpass
import sys
from common import Exceptions

# Used to pass test parameters given on command line to the configuration files
class Parameters(dict):
    def __init__(self):
        self._prompt_parameters = False

    def prompt_parameters(self, set = True):
        self._prompt_parameters = set

    def get_secure(self, key):
        return self._get_param(key, secure=True)


    def __getitem__(self, key):
        return self._get_param(key, secure=False)

    def _get_param(self, key, secure):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if not self._prompt_parameters:
                raise Exceptions.ConfigurationError("Requested parameter '%s' was not defined." % key)

            value = self._prompt(key, secure)
            self[key] = value
            return value

    def _prompt(self, key, secure):
        print "No value set for requested '%s' parameter. Please provide it now." % key

        if secure:
            print "Note that secure value has been requested. The input you type won't be echoed to the screen."
            return getpass.getpass('%s = ' % key)
        else:
            return raw_input("%s = " % key)

parameters = Parameters()
