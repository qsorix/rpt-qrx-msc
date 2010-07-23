#!/usr/bin/env python

from BaseMixins import NamedMixin

class Resource(NamedMixin):
    """Base class for resources.

    Implement transfer_with_<frontend> in your subclasses."""
    def transfer_with_daemon(self, daemon):
        raise NotImplementedError('Implement transfer_with_daemon method in your subclasses.')


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
