#!/usr/bin/env python
# coding=utf-8

import getpass
from common import Exceptions

parameters = None
"""Globalny obiekt udostępniający parametry podane w linii polecenia
programu.
"""

class Parameters(dict):
    """Parametry testu.

    Klasa udostępnia możliwość pytania o parametry, które nie zostały podane
    przy uruchamianiu programu.

    .. method:: parameters[key]
                get(key)

       Pobierz wartość parametru `key`.
    """

    def __init__(self):
        self._prompt_parameters = False

    def get_secure(self, key):
        """ Pobierz wartość parametru `key` w bezpieczny sposób.

        Od zwykłego :meth:`get` różni się to tym, że na terminalach, które to
        obsługują, nie zostanie wyświetlona wartość wprowadzana przez
        użytkownika.
        """
        return self._get_param(key, secure=True)

    def prompt_parameters(self, set = True):
        """
        Włącz pytanie o brakujące parametry. Lub wyłącz, jeśli `set` jest równe
        ``False``.

        Użytkownik będzie miał możliwość wprowadzenia wartości poprzez
        terminal, w którym uruchomił program.
        """
        self._prompt_parameters = set


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
