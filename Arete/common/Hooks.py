#!/usr/bin/env python
# coding=utf-8

from common.PluginMount import PluginMount
from common import Exceptions

class HookPlugin:
    """
    Klasa bazowa dla wtyczek typu Hook. Dziedziczenie z niej powoduje
    automatyczną rejestrację wtyczki. Użytkownik uruchamiając test określa,
    które z wtyczek Hook należy wykonać.


    Imlementacja musi udostępniać wartość atrybutów:

    ===========  ==========================================================
    hook_name    Unikalny napis pozwalający na identyfikację i wybór danej
                 wtyczki.
    ===========  ==========================================================

    .. method:: visit_configured_test(configured_test)

      Metoda uruchamiana po wykonaniu całego kodu mającego wpływ na tworzoną
      konfigurację testu. Parametr `configured_test` typu
      :class:`~config.Configuration.ConfiguredTest`. Zawiera wynikową
      konfigurację, którą można dowolnie modyfikować.

      Konfiguracja jest następnie przekazywana do modułu Controller w celu
      wykonania testu.
    """
    __metaclass__ = PluginMount

    @staticmethod
    def lookup(name):
        for hook in HookPlugin.plugins:
            if hook.hook_name == name: 
                return hook

        raise Exceptions.MissingPluginError("Can't find a plugin for a hook named '%s'." % name)
