#!/usr/bin/env python

class Resources:
    def __init__(self):
        self.__resources = {}

    def add_resource(self, name, resource):
        self.__resources[name] = resource
        return resource

resources = Resources()

add_resource = resources.add_resource

public_functions = {
        'add_resource': add_resource
        }
