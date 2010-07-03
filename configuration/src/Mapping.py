#!/usr/bin/env python

class Mapping:
    def __init__(self):
        self.__bindings = []

    def bind(self, first, second):
        first.bind(second)
        second.bind(first)

        b = sorted([first, second])
        self.bindings().append(b)

    def bindings(self): return self.__bindings

mapping = Mapping()
bind = mapping.bind

public_functions = {
        'bind': bind
    }
