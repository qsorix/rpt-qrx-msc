#!/usr/bin/env python
# coding=utf-8

from BaseMixins import NamedMixin

class Resource(NamedMixin):
    """Base class for resources.

    Implement transfer_with_<frontend> in your subclasses."""
    # FIXME: remove this. it is not pythonish, nor good OOP to raise
    # NotImplementedError. Java does it and we all know it sucks
    def transfer_with_arete_slave(self, frontend):
        raise NotImplementedError('Implement transfer_with_arete_slave method in your subclasses.')

    def generate_commands(self, cmd, host):
        """
        Allows Resource objects to generate additional commands on hosts where
        given resource will be used.

        #cmd is Generator.HostCommands instance with commands for the host. You
        should append only to check, setup i clean.

        #host is passed too so you can check host.model and host.device
        attributes in order to generate commands for proper shell.
        """
        pass


class Resources:
    def __init__(self):
        self._resources = {}

    def add_resource(self, resource):
        self._resources[resource['name']] = resource
        return resource

    def resources(self):
        return self._resources

resources = Resources()

add_resource = resources.add_resource

public_functions = {
    'add_resource': add_resource
}
