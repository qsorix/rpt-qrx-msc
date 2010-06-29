#!/usr/bin/env python

class Mapping:
    def __init__(self):
        self.__bindings = []

    def bind(self, model_host, network_host):
        h = Host(model_host, network_host)
        self.bindings().append(h)
        return h

    def bindings(self): return self.__bindings

class Host:
    def __init__(self, model_host, network_host):
        self.__model = model_host
        self.__network = network_host

    def model(self): return self.__model
    def network(self): return self.__network
    def schedule(self): return self.__schedule

mapping = Mapping()
bind = mapping.bind

public_functions = {
        'bind': bind
    }
