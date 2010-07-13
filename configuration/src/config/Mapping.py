#!/usr/bin/env python

from BaseMixins import NamedMixin
from common import Exceptions

class Mapping(NamedMixin):
    def __init__(self, name):
        self.rename(name)
        self._bindings = set()

    def bind(self, first, second):
        first.bind(second)
        second.bind(first)

        b = tuple(sorted([first, second]))
        self.bindings().add(b)

    def bindings(self): return self._bindings

    def clear(self):
        for (a, b) in self._bindings:
            a.unbind()
            b.unbind()
        self._bindings = set()

_mapping = None

def create_mapping(name):
    global _mapping
    if _mapping:
        raise Exceptions.ConfigurationError('You cannot create more than one mapping.')
    _mapping = Mapping(name)

def destroy_mapping():
    global _mapping
    if _mapping:
        _mapping.clear()

    _mapping = None

def get_mapping():
    global _mapping
    return _mapping

def bind(*args, **kwargs):
    m = get_mapping()
    if m is None:
        raise Exceptions.ConfigurationError('There is no mapping. Did you forget to call \'create_mapping(name)\' before calling bind?')

    return m.bind(*args, **kwargs)

public_functions = {
    'bind': bind,
    'create_mapping': create_mapping,
    'get_mapping': get_mapping
}
