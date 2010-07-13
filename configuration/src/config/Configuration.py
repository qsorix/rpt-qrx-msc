#!/usr/bin/env python

import Model
import Laboratory
import Mapping
import Schedule
import Resources
import common.Exceptions as Exceptions

import traceback

class ConfiguredHost:
    def __init__(self):
        self.model = None
        self.device = None
        self.schedule = None
        self.resources = []
        self.commands = None

class ConfiguredTest:
    """
    Structure to easily pass test configuration.

    attributes:
        hosts - dictionary of ConfiguredHost objects (keys are names from
                Host.model.name()

        resources - dictionary of resources (keys are names from
                    resource.name()
    """

    def sanity_check(self):
        if not Model.get_model():
            raise Exceptions.SanityError("No model defined. You need to create a model. Did you forget to use 'create_model(name)' in your configuration?")

        if not Laboratory.get_laboratory():
            raise Exceptions.SanityError("No laboratory defined. You need to create a laboratory. Did you forget to use 'create_laboratory(name)' in your configuration?")

        if not Mapping.get_mapping():
            raise Exceptions.SanityError("No mapping defined. You need to create a mapping. Did you forget to use 'create_mapping(name)' in your configuration?")

        if not Schedule.get_schedule():
            raise Exceptions.SanityError("No schedule defined. You need to create a schedule. Did you forget to use 'create_schedule(name)' in your configuration?")

        for (name, host) in self.hosts.items():
            if name != host.model.name():
                raise Exceptions.SanityError("Key name is different than element's name")

            if not host.model.bound():
                raise Exceptions.SanityError("Model host '%s' is not bound" % host.name())

            device = host.device

            obligatory_attributes = ['connection', 'frontend']

            for attr in obligatory_attributes:
                if attr not in device.attributes():
                    raise Exceptions.SanityError("Device '%s' doesn't specify '%s' attribute" % (device.name(), attr))

            for (iname, interface) in host.model.interfaces().items():
                if iname != interface.name():
                    raise Exceptions.SanityError("Key's name is different than element's name")

                if not interface.bound():
                    raise Exceptions.SanityError("Interface '%s' of model host '%s' is not bound" % (iname, name))

class Configuration:
    def __init__(self):
        self._configured_test = []

    def read(self, files):

        globals = {}
        globals.update(Model.public_functions)
        globals.update(Laboratory.public_functions)
        globals.update(Mapping.public_functions)
        globals.update(Schedule.public_functions)
        globals.update(Resources.public_functions)
        locals  = {}

        for file in files:
            try:
                execfile(file, globals, locals)
            except Exception as e:
                raise Exceptions.ConfigurationError(e, traceback=traceback.format_exc())

        self._combine_hosts()

        return self.configured_test()
    
    def _combine_hosts(self):
        ct = ConfiguredTest()
        ct.resources = Resources.resources.resources()
        ct.hosts = {}

        for h in Model.get_model().hosts():
            host = ConfiguredHost()
            host.model = h
            host.device = h.bound()
            host.schedule = Schedule.get_schedule().host_schedule(h.name())
            host.resources = set(h.needed_resources())
            for event in host.schedule:
                host.resources.update(event.command().needed_resources())

            ct.hosts[h.name()] = host

        self._configured_test = ct

    def configured_test(self):
        return self._configured_test

