#!/usr/bin/env python

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin
from common import Exceptions

class Laboratory(NamedMixin):
    def __init__(self, name):
        self.rename(name)
        self._devices = []

    def devices(self): return self._devices

    def add_device(self, *args, **kwargs):
        d = Device(*args, **kwargs)
        for device in self.devices():
            if d['name'] == device['name']:
                raise Exceptions.NameExistsError('Device ' + d['name'] + ' is already defined for this laboratory.')

        self.devices().append(d)
        return d

    def clear(self):
        self._devices = []

class Device(NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin):
    def __init__(self, name, **kwargs):
        self.rename(name)
        self.set_attributes(**kwargs)

_laboratory = None

def create_laboratory(name):
    global _laboratory
    if _laboratory:
        raise Exceptions.ConfigurationError('You cannot create more than one laboratory.')

    _laboratory = Laboratory(name)

def destroy_laboratory():
    global _laboratory
    if _laboratory:
        _laboratory.clear()

    _laboratory = None

def get_laboratory():
    global _laboratory
    return _laboratory

def add_device(*args, **kwargs):
    d = get_laboratory()
    if d is None:
        raise Exceptions.ConfigurationError('There is no laboratory. Did you forget to call \'create_laboratory(name)\' before calling add_device?')
    return d.add_device(*args, **kwargs)

public_functions = {
    'create_laboratory': create_laboratory,
    'get_laboratory': get_laboratory,
    'add_device': add_device
}
