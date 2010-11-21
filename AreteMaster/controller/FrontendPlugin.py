#!/usr/bin/env python
# coding=utf-8

from AreteMaster.common.PluginMount import PluginMount

class FrontendPlugin:
    """
    Klasa bazowa dla wtyczek typu Frontend. Dziedziczenie z tej klasy powoduje
    automatyczną rejestrację wtyczki.


    Wtyczki implementujące ten interfejs mają udostępniać wartości następujących atrybutów:

    .. attribute:: frontend_type

        Napis określający typu frontendu implementowanego przez wtyczkę.
        Zostanie on dopasowany do atrybutu 'frontend' urządzenia
        konfigurowanego w laboratorium.
                      

    .. attribute:: needed_attributes

        Lista atrybutów, które mają być określone dla urządzenia, aby działanie
        wtyczki było poprawne. Framework odrzuci konfigurację jeżeli wymienione tu
        atrybuty nie zostanę określone.

       Domyślnie [].

    .. method:: deply_configuration()

       Prześlij konfigurację na kontrolowane urządzenie.

    .. method:: start_sanity_check()

       Prześlij do kontrolowanego urządzenia rozkaz rozpoczęcia sprawdzania
       poprawności konfiguracji. Metoda powinna wrócić natychmiast.

       Opcjonalnym zachowaniem jest implementacja w tej metodzie synchronizacji
       czasu z kontrolowanym urządzeniem. Z obliczonej różnicy czasowej należy
       potem skorzystać w momencie uruchamiania testu.

    .. method:: wait_sanity_check()

       Zaczekaj aż kontrolowane urządzenie zakończy sprawdzania poprawności
       konfiguracji. W przypadku stwierdzenia nieprawidłowości zgłoszone ma to
       być wyjątkiem typu `Exceptions.SanityError`.

    .. method:: start_test(duration_policy)

       Rozpocznij wykonywać test. Przekazany obiekt `duration_policy`
       udostępnia metody `start()` oraz `end_policy()` określające godzinę
       rozpoczęcia testu oraz sposób jego zakończenia określony w konfiguracji.

    .. method:: check_test_end()

       Wykonywane periodycznie w czasie trwania testu aż do momentu, kiedy
       zwróci `True`. Jeżeli frontend utrzymuje połączenie z kontrolowanym
       urządzeniem, w metodzie tej może dokonywać komunikacji, pod warunkiem,
       że wykonanie metody nie będzie miało charakteru blokującego.

    .. method:: fetch_results()

       Pobierz wyniki testu. Uruchamiane po zakończeniu testu na wszystkich
       urządzeniach.

    .. method:: abort_test()

       Jeżeli któryś z frontendów zgłosi błąd, metoda ta jest wykonywana na
       wszystkich frontendach, dając im możliwość przerwania wykonywanego
       testu.

    .. method:: trigger(name)

       Przekaż urządzeniu, że wyzwalacz o nazwie `name` został aktywowany.
    """

    needed_attributes = []

    __metaclass__ = PluginMount

    @staticmethod
    def lookup(name):
        for p in FrontendPlugin.plugins:
            if p.frontend_type == name:
                return p

        raise RuntimeError("Frontend plugin for type '%s' was not registered" % name)

    def __init__(self, host, connection_class, configured_test, **kwargs):
        self._host = host
        self._configured_test = configured_test
        self._connection_class = connection_class
        self._connection = connection_class(self.host())

    def configuration(self):
        return self._configured_test

    def connection(self):
        return self._connection

    def output(self):
        assert self._connection
        return self._connection.output()

    def input(self):
        assert self._connection
        return self._connection.input()

    def connect(self):
        self._connection.connect()

    def disconnect(self):
        if self._connection:
            self._connection.close()

    def host(self):
        return self._host

    # FIXME: remove these, it is not pythonish
    def start_sanity_check(self):
        pass

    def wait_sanity_check(self):
        pass

    def deploy_configuration(self, host_configuration):
        pass

    def start_test(self, duration_policy):
        pass

    def wait_test(self):
        pass

    def fetch_results(self):
        pass

    def abort_test(self):
        pass

 
