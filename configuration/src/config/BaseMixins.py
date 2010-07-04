#!/usr/bin/env python

import Exceptions

class AttributedMixin:
    def get(self, name):
        return self.__attributes[name]

    def attributes(self, **kwargs):
        try:
            self.__attributes.update(kwargs)
        except AttributeError:
            self.__attributes = kwargs

        return self.__attributes

class NamedMixin:
    def rename(self, name):
        self.__name = name

    def name(self):
        return self.__name

class BindableMixin:
    def bind(self, bindable):
        self.__bound_with = bindable

    def bound(self):
        try:
            return self.__bound_with
        except AttributeError:
            return None

    def unbind(self):
        self.__bound_with = None

class InterfacesMixin:
    class Interface(NamedMixin, AttributedMixin, BindableMixin):
        def __init__(self, host, name, **kwargs):
            self.__host = host
            self.rename(name)
            self.attributes(**kwargs)

        def host(self):
            return self.__host

    def add_interface(self, name, **attributes):
        i = InterfacesMixin.Interface(self, name, **attributes)
        try:
            if name in self.__interfaces:
                raise Exceptions.NameExistsError('Interface ' + name + ' is already defined.')

            self.__interfaces[i.name()] = i

        except AttributeError:
            self.__interfaces = {i.name(): i}

        return i

    def interfaces(self):
        try:
            return self.__interfaces
        except AttributeError:
            self.__interfaces = {}
            return self.__interfaces

    def interface(self, name):
        try:
            return self.__interfaces[name]
        except AttributeError:
            self.__interfaces = {}
            return self.__interfaces[name]
            
