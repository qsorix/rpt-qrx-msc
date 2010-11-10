#!/usr/bin/env python
# coding=utf-8

from BaseMixins import NamedMixin, InterfacesMixin
from common import Exceptions
import Utils

class Mapping(NamedMixin):
    """Mapowanie między modelem a laboratorium."""

    def __init__(self, name):
        self.rename(name)
        self._bindings = set()

    def bind(self, model_object, laboratory_object):
        """Powiąż obiekt z modelu z obiektem z laboratorium.

        Obiekty mogą być przekazane przez nazwy podane przy ich tworzeniu.
        Nazwy interfejsów należy podawać z kropką np. ``"<nazwa
        urządzenia>.<nazwa interfejsu>"``.

        """
        if isinstance(model_object, str):
            model_object = Utils.resolve_name(model_object, model=True)

        if isinstance(laboratory_object, str):
            laboratory_object = Utils.resolve_name(laboratory_object, laboratory=True)

        if (isinstance(model_object, InterfacesMixin.Interface) != isinstance(laboratory_object, InterfacesMixin.Interface)):
            raise Exceptions.ConfigurationError('You can only bind interface with an interface, not with host or device.')

        model_object.bind(laboratory_object)
        laboratory_object.bind(model_object)

        b = tuple(sorted([model_object, laboratory_object]))
        self.bindings().add(b)

    def bindings(self):
        """Zwróć zdefiniowane powiązania."""
        return self._bindings

    def clear(self):
        """Usuń zdefiniowane powiązania."""
        for (a, b) in self._bindings:
            a.unbind()
            b.unbind()
        self._bindings = set()

_mapping = None

def create_mapping(name):
    """Stwórz mapowanie o nazwie `name`.

    Obecna implementacja dopuszcza w konfiguracji istnienie tylko jednego
    mapowania.
    """
    global _mapping
    if _mapping:
        raise Exceptions.ConfigurationError('You cannot create more than one mapping.')
    _mapping = Mapping(name)

def destroy_mapping():
    global _mapping
    if _mapping:
        _mapping.clear()

    _mapping = None

def get_mapping(validate=True):
    """Zwróć mapowanie.

    Funkcja rzuca wyjątek, jeśli mapowanie nie zostało utworzone. Jeśli w argumencie
    `validate` przekazano ``False`` wyjątek nie będzie rzucony i funkcja zwróci None.

    """
    global _mapping
    if validate and _mapping is None:
        raise Exceptions.ConfigurationError('There is no mapping. Did you forget to call \'create_mapping(name)\'?')
    return _mapping

def bind(*args, **kwargs):
    """Powiąż obiekty.

    Patrz :meth:`Mapping.bind() <config.Mapping.Mapping.bind>`.
    """
    m = get_mapping()
    return m.bind(*args, **kwargs)

public_functions = {
    'bind': bind,
    'create_mapping': create_mapping,
    'get_mapping': get_mapping
}
