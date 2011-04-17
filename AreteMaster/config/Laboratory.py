#!/usr/bin/env python
# coding=utf-8

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin
from common import Exceptions

class Laboratory(NamedMixin):
    """Konfiguracja laboratorium."""

    def __init__(self, name):
        self.rename(name)
        self._devices = []

    def devices(self):
        """Zwróć listę zdefiniowanych urządzeń."""
        return self._devices

    def add_device(self, *args, **kwargs):
        """Dodaj urządzenie do laboratorium.

        Wszystkie argumenty przekazywane są do konstruktora tworzonego urządzenia
        (:class:`~config.Laboratory.Device`). Metoda zwraca referencję do
        dodanego urządzenia.

        """
        d = Device(*args, **kwargs)
        for device in self.devices():
            if d['name'] == device['name']:
                raise Exceptions.NameExistsError('Device ' + d['name'] + ' is already defined for this laboratory.')

        self.devices().append(d)
        return d

    def clear(self):
        """ Usuń z laboratorium wszystkie urządzenia.
        Nie powinieneś używać tej metody chyba, że wiesz co robisz.
        
        """
        self._devices = []

class Device(NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin):
    """Urządzenie w laboratorium."""
    def __init__(self, name, **kwargs):
        """Stwórz urządzenie o nazwie `name` przypisując mu atrybuty przekazane
        w `kwargs`.
        """
        self.rename(name)
        self.set_attributes(**kwargs)

_laboratory = None

def create_laboratory(name):
    """Stwórz laboratorium o nazwie `name`.

    Obecna implementacja dopuszcza istnienie tylko jednego laboratorium.
    """
    global _laboratory
    if _laboratory:
        raise Exceptions.ConfigurationError('You cannot create more than one laboratory.')

    _laboratory = Laboratory(name)

def destroy_laboratory():
    global _laboratory
    if _laboratory:
        _laboratory.clear()

    _laboratory = None

def get_laboratory(validate=True):
    """Zwróć laboratorium.

    Funkcja rzuca wyjątek, jeśli laboratorium nie zostało utworzone. Jeśli w argumencie
    `validate` przekazano ``False`` wyjątek nie będzie rzucony i funkcja zwróci None.
    """
    global _laboratory
    if validate and _laboratory is None:
        raise Exceptions.ConfigurationError('There is no laboratory. Did you forget to call \'create_laboratory(name)\'?')

    return _laboratory

def add_device(*args, **kwargs):
    """Stwórz i dodaj urządzenie do modelu.

    Patrz :meth:`Laboratory.add_device <config.Laboratory.Laboratory.add_device>`.
    """
    d = get_laboratory()
    return d.add_device(*args, **kwargs)

public_functions = {
    'create_laboratory': create_laboratory,
    'get_laboratory': get_laboratory,
    'add_device': add_device
}
