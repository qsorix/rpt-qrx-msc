#!/usr/bin/env python

from BaseMixins import NamedMixin, AttributedMixin, InterfacesMixin, BindableMixin
from common import Exceptions
import Utils
import Resources

class Model(NamedMixin):
    def __init__(self, name):
        self.rename(name)
        self._hosts = []
        self._links = []

    def hosts(self): return self._hosts
    def links(self): return self._links

    def add_host(self, *args, **kwargs):
        h = Host(*args, **kwargs)
        for host in self.hosts():
            if h['name'] == host['name']:
                raise Exceptions.NameExistsError('Host ' + h['name'] + ' is already defined for the model.')

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
        self.set_attributes(**kwargs)
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
        if isinstance(first_interface, str):
            first_interface = Utils.resolve_interface_name(first_interface, model=True)

        if isinstance(second_interface, str):
            second_interface = Utils.resolve_interface_name(second_interface, model=True)

        self._first = first_interface
        self._second = second_interface

    def first(self):
        return self._first

    def second(self):
        return self._second

_model = None

def create_model(name):
    global _model
    if _model:
        raise Exceptions.ConfigurationError('You cannot create more than one model.')
    _model = Model(name)

def destroy_model():
    global _model
    if _model:
        _model.clear()
    _model = None

def get_model(validate=True):
    global _model
    if validate:
        if _model is None:
            raise Exceptions.ConfigurationError('There is no model. Did you forget to call \'create_model(name)\'?')
    return _model

def add_host(name, **kwargs):
    """
    Creates new host with given *name* and adds it to the model. All *kwargs*
    will be set for that host. Returns created host.
    """
    return get_model().add_host(name, **kwargs)

def add_link(*args, **kwargs):
    return get_model().add_link(*args, **kwargs)

public_functions = {
    'create_model': create_model,
    'get_model': get_model,
    'add_host': add_host,
    'add_link': add_link
}
