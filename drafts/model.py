#!/usr/bin/env python

class Model():
    def host(self, name, count=1):
        return Host(name)

    def link(self, *args):
        return link(*args)

    def link_all(self, *args):
        return link(args)

class Host():
    def __init__(self, name):
        self.name = name
        self.interfaces = {'default': Interface()}

    def __getattr__(self, name):
        return self.interfaces.setdefault(name, Interface())

    def __repr__(self):
        return "Host(" + self.name + ")"

    def __getitem__(self, key):
        return self.interfaces.setdefault(key, Interface())

class Interface():
    def __init__(self):
        self.parameters = {}

    def __call__(self, **parameters):
        self.parameters.update(parameters)

def link(hosts):
    print "link locals:  ", locals()
    print "link globals: ", globals().keys()
    print "link linking: ", hosts

def model(name):
    print "model: ", name

