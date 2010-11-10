#!/usr/bin/env python
# coding=utf-8

from common import Exceptions

class AttributedMixin:
    """Obsługa atrybutów."""

    def __contains__(self, name):
        return name in self._attributes

    def __getitem__(self, name):
        """Zwróć wartość atrybutu ``name``.

        Zwróci ``None`` jeśli podany atrybut nie został określony.
        """
        try:
            if name in self._attributes:
                return self._attributes[name]
            else:
                return None
        except AttributeError:
            return None

    def set_attributes(self, **kwargs):
        """ Ustaw wartości przekazanych atrybutów.

        Jeżeli podane atrybuty już występują, ich wartości są zastępowane.
        """
        try:
            self._attributes.update(kwargs)
        except AttributeError:
            self._attributes = kwargs

    def attributes(self):
        """Zwróć nazwy zdefiniowanych atrybutów."""
        try:
            return self._attributes.keys()
        except AttributeError:
            return []

class NamedMixin(AttributedMixin):
    def rename(self, new_name):
        self.set_attributes(name=new_name)

class BindableMixin:
    def bind(self, bindable):
        """Powiąż z przekazanym obiektem.

        Aby nie naruszyć poprawności modelu, powinieneś powiązywać obiekty
        modelu z obiektami laboratorium: hosty z urządzeniami i odpowiadające
        sobie interfejsy.
        
        """
        self._bound_with = bindable

    def bound(self):
        """Zwróć powiązany obiekt.

        Zwraca ``None`` jeśli żaden obiekt nie został związany.

        """
        try:
            return self._bound_with
        except AttributeError:
            return None

    def unbind(self):
        """Usuń powiązanie."""
        self._bound_with = None

class InterfacesMixin:
    class Interface(NamedMixin, AttributedMixin, BindableMixin):
        """Interfejs sieciowy."""

        def __init__(self, host, name, **kwargs):
            """
            Interfejs zostanie nazwany `name`. Przekazany `host` ma być
            hostem lub urządzeniem, do którego dodany będzie tworzony
            interfejs.  Korzystając z `kwargs` można jednocześnie zdefiniować
            atrybuty interfejsu.

            Nie powinieneś samodzielnie tworzyć interfejsów. Skorzystaj z metod
            :meth:`Host.add_interface() <config.Model.Host.add_interface>` lub
            :meth:`Device.add_interface() <config.Laboratory.Device.add_interface>`.
            """
            self._host = host
            self.rename(name)
            self.set_attributes(**kwargs)

        def host(self):
            """Zwróć właściciela interfejsu."""
            return self._host

    def add_interface(self, name, **attributes):
        """Dodaj interfejs `name`.

        Za pomocą argumentu `attributes` można jednocześnie zdefiniować
        atrybuty tworzonego interfejsu. Zwracana jest referencja do nowego
        interfejsu.
        
        """
        i = InterfacesMixin.Interface(self, name, **attributes)
        try:
            if name in self._interfaces:
                raise Exceptions.NameExistsError('Interface ' + name + ' is already defined.')

            self._interfaces[i['name']] = i

        except AttributeError:
            self._interfaces = {i['name']: i}

        return i

    def interfaces(self):
        """Zwróć zdefiniowane interfejsy."""
        try:
            return self._interfaces
        except AttributeError:
            self._interfaces = {}
            return self._interfaces

    def interface(self, name):
        """Zwróć interfejs nazwany `name`."""
        try:
            return self._interfaces[name]
        except AttributeError:
            self._interfaces = {}
            return self._interfaces[name]
            
