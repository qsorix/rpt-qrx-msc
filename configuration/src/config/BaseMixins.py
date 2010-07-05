#!/usr/bin/env python

import Exceptions

class AttributedMixin:
    def get(self, name):
        return self._attributes[name]

    def attributes(self, **kwargs):
        try:
            self._attributes.update(kwargs)
        except AttributeError:
            self._attributes = kwargs

        return self._attributes

class NamedMixin:
    def rename(self, name):
        self._name = name

    def name(self):
        return self._name

class BindableMixin:
    def bind(self, bindable):
        self._bound_with = bindable

    def bound(self):
        try:
            return self._bound_with
        except AttributeError:
            return None

    def unbind(self):
        self._bound_with = None

class InterfacesMixin:
    class Interface(NamedMixin, AttributedMixin, BindableMixin):
        def __init__(self, host, name, **kwargs):
            self._host = host
            self.rename(name)
            self.attributes(**kwargs)

        def host(self):
            return self._host

    def add_interface(self, name, **attributes):
        i = InterfacesMixin.Interface(self, name, **attributes)
        try:
            if name in self._interfaces:
                raise Exceptions.NameExistsError('Interface ' + name + ' is already defined.')

            self._interfaces[i.name()] = i

        except AttributeError:
            self._interfaces = {i.name(): i}

        return i

    def interfaces(self):
        try:
            return self._interfaces
        except AttributeError:
            self._interfaces = {}
            return self._interfaces

    def interface(self, name):
        try:
            return self._interfaces[name]
        except AttributeError:
            self._interfaces = {}
            return self._interfaces[name]
            
