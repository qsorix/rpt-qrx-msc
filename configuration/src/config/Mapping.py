#!/usr/bin/env python

class Mapping:
    def __init__(self):
        self.__bindings = set()

    def bind(self, first, second):
        first.bind(second)
        second.bind(first)

        b = tuple(sorted([first, second]))
        self.bindings().add(b)

    def bindings(self): return self.__bindings

    def clear(self):
        for (a, b) in self.__bindings:
            a.unbind()
            b.unbind()
        self.__bindings = set()

mapping = Mapping()
bind = mapping.bind

public_functions = {
        'bind': bind
    }
