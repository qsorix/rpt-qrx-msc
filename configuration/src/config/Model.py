#!/usr/bin/env python

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin
import common.Exceptions
import Resources

class Model:
    def __init__(self):
        self._hosts = []
        self._links = []

    def hosts(self): return self._hosts
    def links(self): return self._links

    def add_host(self, *args, **kwargs):
        h = Host(*args, **kwargs)
        for host in self.hosts():
            if h.name() == host.name():
                raise Exceptions.NameExistsError('Host ' + h.name() + ' is already defined for the model.')

        self.hosts().append(h)
        return h

    def add_link(self, *args, **kwargs):
        l = Link(*args, **kwargs)
        self.links().append(l)
        return l

    def clear(self):
        self._hosts = []

class Host(NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin):
    def __init__(self, name, **kwargs):
        self.rename(name)
        self.attributes(**kwargs)
        self._resources = set()

    def use_resource(self, resource_name):
        resource = Resources.resources.resources()[resource_name]
        self._resources.add(resource)

    def needed_resources(self):
        return self._resources

class Link:
    """Connection between hosts.

    Link models ability of two hosts two communicate using specified
    interfaces."""

    def __init__(self, first_interface, second_interface):
        self._first = first_interface
        self._second = second_interface

    def first(self):
        return self._first

    def second(self):
        return self._second

model = Model()
add_host = model.add_host
add_link = model.add_link

public_functions = {
        'add_host': add_host,
        'add_link': add_link
}

