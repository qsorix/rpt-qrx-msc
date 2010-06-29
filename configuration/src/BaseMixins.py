#!/usr/bin/env python

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

class InterfacesMixin:
    class Interface(NamedMixin, AttributedMixin):
        def __init__(self, host, name, **kwargs):
            self.__host = host
            self.rename(name)
            self.attributes(**kwargs)

        def host(self):
            return self.__host

    def interface(self, name, **attributes):
        i = InterfacesMixin.Interface(self, name, **attributes)
        try:
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
            
