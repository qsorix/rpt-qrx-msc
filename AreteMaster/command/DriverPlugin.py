#!/usr/bin/env python
# coding=utf-8

from common.PluginMount import PluginMount

class HostDriverPlugin:
    """
    Klasa bazowa dla wtyczek sterowników parametrów hosta. Dziedziczenie z niej
    powoduje automatyczną rejestrację wtyczki.

    Sterownik parametrów hosta to wtyczka, która, na podstawie atrybutów
    skonfigurowanych hostów, tworzy komendy, które w czasie wykonania
    konfigurują środowisko urządzenia zgodnie z wartościami atrybutów.

    Wtyczka użytkownika musi udostępniać metodę:

    .. method:: process(cmd, host, attributes)

      Zostanie uruchomiona dla każdego hosta z konfiguracji. Parametr
      `attributes` jest zestawem atrybutów, które jeszcze nie zostały
      obsłużone. Sterownik ma usuwać nazwy atrybutów, dla których stworzył
      komendy.
      
      Parametr `cmd` to budowany obiekt
      (:class:`~command.Generator.HostCommands`) zawierający komendy. Parametr
      `host` typu :class:`~config.Configuration.ConfiguredHost`, umożliwia dostęp do
      odwzorowanego urządzenia. 
    """
    __metaclass__ = PluginMount


class InterfaceDriverPlugin:
    """
    Klasa bazowa dla wtyczek sterowników parametrów interfejsu. Dziedziczenie z
    niej powoduje automatyczną rejestrację wtyczki.

    Sterownik parametrów interfejsu to wtyczka, która, na podstawie atrybutów
    skonfigurowanego interfejsu, tworzy komendy, które w czasie wykonania konfigurują
    środowisko urządzenia zgodnie z wartościami atrybutów.

    Wtyczka użytkownika musi udostępniać metodę:

    .. method:: process(cmd, host, interface, attributes)

      Zostanie uruchomiona dla każdego interfejsu z konfiguracji. Parametr
      `attributes` jest zestawem atrybutów, które jeszcze nie zostały
      obsłużone. Sterownik ma usuwać nazwy atrybutów, dla których stworzył
      komendy.
      
      Parametr `cmd` to budowany obiekt
      (:class:`~command.Generator.HostCommands`) zawierający komendy. Parametr
      `host` typu :class:`~config.Configuration.ConfiguredHost`, umożliwia dostęp do
      odwzorowanego urządzenia. Natomiast parametr `interface` to interfejs dla
      którego została uruchomiona metoda process.
    """
    __metaclass__ = PluginMount

