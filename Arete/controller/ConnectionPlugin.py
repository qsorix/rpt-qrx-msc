#!/usr/bin/env python
# coding=utf-8

from common.PluginMount import PluginMount

class ConnectionPlugin:
    """
    Klasa bazowa dla wtyczek typu Connection, służących do zestawiania połączeń
    z urządzeniami.

    Wtyczki implementujące ten interfejs muszą definiować wartości atrybutów:

    =================  =======================================================
    connection_type    String pozwalający w konfiguracji laboratorium
                       jednoznacznie wybrać daną wtyczkę, używając atrybutu
                       'connection' urządzenia.

    needed_attributes  List atrybutów, które maja być określone dla urządzenia
                       korzystającego z danej wtyczki. Framework odrzuci
                       konfigurację, w której atrybuty nie będą występować.

                       Domyślnie [].
    =================  =======================================================

    W czasie tworzenia obiektu, konstruktor otrzymuje host, na rzecz którego
    będzie używana dana instacja. Połączenie ma być nawiązywane korzystając
    parametrów określanych przez atrybuty odwzorowanego urządzenia.

    .. method:: connect()

       Zestaw połączenie.

    .. method:: disconnect()

       Zamknij połączenie.

    .. method:: setblocking(blocking)

       Ustaw flagę określającą blokujący (lub nie, w przypadku przekazania
       wartości `False`) tryb czytania. Jeśli wyłączono tryb blokowania,
       wykonywanie metod `input` lub `output` ma natychmiast wracać.

    .. method:: input()

       Zwróć obiekt posiadający interfejs analogiczny do `file` i umożliwiający
       czytanie.

    .. method:: output()

       Zwróć obiekt posiadający interfejs analogiczny do `file` i umożliwiający
       pisanie.
    """
    needed_attributes = []

    __metaclass__ = PluginMount

    @staticmethod
    def lookup(name):
        for p in ConnectionPlugin.plugins:
            if p.connection_type == name:
                return p

        raise RuntimeError("Connection plugin for type '%s' was not registered" % name)
