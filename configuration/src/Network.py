#!/usr/bin/env python

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin
from Exceptions import ConfigurationError

class Network:
    def __init__(self):
        self.__hosts = []

    def hosts(self): return self.__hosts

    def host(self, *args, **kwargs):
        h = Host(*args, **kwargs)
        self.hosts().append(h)
        return h

class Host(NamedMixin, AttributedMixin, InterfacesMixin):
    def __init__(self, name, **kwargs):
        self.rename(name)
        self.attributes(**kwargs)

network = Network()
host = network.host

public_functions = {
        'host': host
}
