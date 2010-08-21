#!/usr/bin/env python
# coding=utf-8

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin
from common import Exceptions
import Utils
import Resources

class Model(NamedMixin):
    """ Konfiguracja modelu. """

    def __init__(self, name):
        self.rename(name)
        self._hosts = []
        self._links = []

    def hosts(self):
        """ Zwróć listę zdefiniowanych hostów. """
        return self._hosts

    def links(self):
        """ Zwróć listę zdefiniowanych połączeń. """
        return self._links

    def add_host(self, *args, **kwargs):
        """ Dodaj host do modelu.

        Wszystkie argumenty przekazywane są do konstruktora tworzonego hosta
        (:class:`~config.Model.Host`). Metoda zwraca referencję do dodanego
        hosta.
        
        """
        h = Host(*args, **kwargs)
        for host in self.hosts():
            if h['name'] == host['name']:
                raise Exceptions.NameExistsError('Host ' + h['name'] + ' is already defined for the model.')

        self.hosts().append(h)
        return h

    def add_link(self, *args, **kwargs):
        """ Dodaj połączenie do modelu.

        Wszystkie argumenty przekazywane są do konstruktora tworzonego połączenia
        (:class:`~config.Model.Link`). Metoda zwraca referencję do dodanego
        połączenia.
        
        """

        l = Link(*args, **kwargs)
        self.links().append(l)
        return l

    def clear(self):
        """ Usuń z modelu wszystkie obiekty.
        Nie powinieneś używać tej metody chyba, że wiesz co robisz.
        
        """
        self._hosts = []
        self._links = []

class Host(NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin):
    """Modelowany host."""
    def __init__(self, name, **kwargs):
        """Stwórz host nazwany `name` przypisując mu atrybuty przekazane w
        `kwargs`.
        """
        self.rename(name)
        self.set_attributes(**kwargs)
        self._resources = set()

    def use_resource(self, resource_name):
        """Używaj zasobu `resource_name`.

        Powoduje, że w czasie testu na urządzenie odpowiadające hostowi
        zostanie przesłany określony zasób.

        """
        resource = Resources.resources.resources()[resource_name]
        self._resources.add(resource)

    def needed_resources(self):
        """Zwróć listę używanych zasobów."""
        return self._resources

class Link:
    """Połączenie pomiędzy interfejsami."""

    def __init__(self, first_interface, second_interface):
        """
        Tworzy połączenie pomiędzy interfejsami `first_interface` i
        `second_interface`. Oba argumenty mogą być interfejsami zwróconymi z
        :meth:`~config.Model.Host.add_interface` lub łańcuchami w formanie
        ``<nazwa hosta>.<nazwa interfejsu>``.
        """
        if isinstance(first_interface, str):
            first_interface = Utils.resolve_interface_name(first_interface, model=True)

        if isinstance(second_interface, str):
            second_interface = Utils.resolve_interface_name(second_interface, model=True)

        self._first = first_interface
        self._second = second_interface

    def first(self):
        """Zwróć pierwszy interfejs połączenia."""
        return self._first

    def second(self):
        """Zwróć drugi interfejs połączenia."""
        return self._second

_model = None

def create_model(name):
    """Stwórz model o nazwie `name`.

    Obecna implementacja dopuszcza istnienie tylko jednego modelu.
    """
    global _model
    if _model:
        raise Exceptions.ConfigurationError('You cannot create more than one model.')
    _model = Model(name)

def destroy_model():
    global _model
    if _model:
        _model.clear()
    _model = None

def get_model(validate=True):
    """Zwróć model.

    Funkcja rzuca wyjątek, jeśli model nie został utworzony. Jeśli w argumencie
    `validate` przekazano ``False``, w takim wypadku zwróci None.

    """
    global _model
    if validate:
        if _model is None:
            raise Exceptions.ConfigurationError('There is no model. Did you forget to call \'create_model(name)\'?')
    return _model

def add_host(name, **kwargs):
    """Stwórz i dodaj host do modelu.

    Patrz :meth:`Model.add_host <config.Model.Model.add_host>`.
    """
    return get_model().add_host(name, **kwargs)

def add_link(*args, **kwargs):
    """Stwórz w modelu nowe połączenie.

    Patrz :meth:`Model.add_link() <config.Model.Model.add_link>`.
    """
    return get_model().add_link(*args, **kwargs)

public_functions = {
    'create_model': create_model,
    'get_model': get_model,
    'add_host': add_host,
    'add_link': add_link
}
