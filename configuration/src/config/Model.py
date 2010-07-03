#!/usr/bin/env python

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin

class Model:
    def __init__(self):
        self.__hosts = []
        self.__links = []

    def hosts(self): return self.__hosts
    def links(self): return self.__links

    def host(self, *args, **kwargs):
        h = Host(*args, **kwargs)
        self.hosts().append(h)
        return h

    def link(self, *args, **kwargs):
        l = Link(*args, **kwargs)
        self.links().append(l)
        return l

class Host(NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin):
    def __init__(self, name, **kwargs):
        self.rename(name)
        self.attributes(**kwargs)
        self.__resources = set()

    def use_resource(self, resource_name):
        self.__resources.add(resource_name)

    def needed_resources(self):
        return self.__resources

class Link:
    """Connection between hosts.

    Link models ability of two hosts two communicate using specified
    interfaces."""

    def __init__(self, first_interface, second_interface):
        self.__first = first_interface
        self.__second = second_interface

    def first(self):
        return self.__first

    def second(self):
        return self.__second

model = Model()
host = model.host
link = model.link

public_functions = {
        'host': host,
        'link': link
}

