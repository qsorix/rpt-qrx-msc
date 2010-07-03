#!/usr/bin/env python

class File:
    def __init__(self, path):
        self.__path = path

    def path(self):
        return self.__path

    def __repr__(self):
        return 'File(%s)' % repr(self.path())

class Resources:
    def __init__(self):
        self.__resources = {}

    def add_resource(self, name, resource):
        self.__resources[name] = resource
        return resource

    def resources(self):
        return self.__resources

resources = Resources()

add_resource = resources.add_resource

public_functions = {
        'add_resource': add_resource,
        'File': File
        }
