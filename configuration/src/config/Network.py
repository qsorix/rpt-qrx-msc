#!/usr/bin/env python

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin
import Exceptions

class Network:
    def __init__(self):
        self._hosts = []

    def hosts(self): return self._hosts

    def add_host(self, *args, **kwargs):
        h = Host(*args, **kwargs)
        for host in self.hosts():
            if h.name() == host.name():
                raise Exceptions.NameExistsError('Host ' + h.name() + ' is already defined for the network.')

        self.hosts().append(h)
        return h

    def clear(self):
        self._hosts = []

class Host(NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin):
    def __init__(self, name, **kwargs):
        self.rename(name)
        self.attributes(**kwargs)

network = Network()
add_host = network.add_host

public_functions = {
        'add_host': add_host
}
