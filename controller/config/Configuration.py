#!/usr/bin/env python
# coding=utf-8

import Model
import Laboratory
import Mapping
import Schedule
import Resources
import Utils
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
                Host.model['name']

        resources - dictionary of resources (keys are names from
                    resource['name']

        end_policy - information about test ending policy, this string is passed
                     to participating frontends, they should understand it
    """

    def sanity_check(self):
        for (name, host) in self.hosts.items():
            if name != host.model['name']:
                raise Exceptions.SanityError("Key name is different than element's name")

            if not host.model.bound():
                raise Exceptions.SanityError("Model host '%s' is not bound" % host.model['name'])

            device = host.device

            obligatory_attributes = ['connection', 'frontend']

            for attr in obligatory_attributes:
                if not device[attr]:
                    raise Exceptions.SanityError("Device '%s' doesn't specify '%s' attribute" % (device['name'], attr))

            for (iname, interface) in host.model.interfaces().items():
                if iname != interface['name']:
                    raise Exceptions.SanityError("Key's name is different than element's name")

                if not interface.bound():
                    raise Exceptions.SanityError("Interface '%s' of model host '%s' is not bound" % (iname, name))

        if not Schedule.get_schedule().test_end_policy():
            raise Exceptions.SanityError("Test end policy not specified. Use test_end_policy(<policy>) in your configuration.")

class Configuration:
    def __init__(self):
        self._configured_test = []

    def read(self, files, cmdline_mappings):

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

        self._command_line_mappings(cmdline_mappings)

        self._sanity_check()

        self._combine_hosts()

        return self.configured_test()


    def _command_line_mappings(self, mappings):
        if not mappings: return

        #try:
        Mapping.create_mapping('command-line')
        for m in mappings:
            (model, device) = m.split(':')
            Mapping.bind(model, device)

        #except Exception as e:
            #raise e
            #raise Exceptions.ConfigurationError(e, "Could not parse command line mappings {0!r}".format(mappings));

    def _sanity_check(self):
        if not Model.get_model():
            raise Exceptions.SanityError("No model defined. You need to create a model. Did you forget to use 'create_model(name)' in your configuration?")

        if not Laboratory.get_laboratory():
            raise Exceptions.SanityError("No laboratory defined. You need to create a laboratory. Did you forget to use 'create_laboratory(name)' in your configuration?")

        if not Mapping.get_mapping():
            raise Exceptions.SanityError("No mapping defined. You need to create a mapping. Did you forget to use 'create_mapping(name)' in your configuration?")

        if not Schedule.get_schedule():
            raise Exceptions.SanityError("No schedule defined. You need to create a schedule. Did you forget to use 'create_schedule(name)' in your configuration?")
    
    def _combine_hosts(self):
        ct = ConfiguredTest()
        ct.resources = Resources.resources.resources()
        ct.hosts = {}
        ct.end_policy = Schedule.get_schedule().test_end_policy()
        ct.setup_phase_delay = Schedule.get_schedule().setup_phase_delay()

        for h in Model.get_model().hosts():
            host = ConfiguredHost()
            host.model = h
            host.device = h.bound()
            host.schedule = Schedule.get_schedule().host_schedule(h['name'])

            resources = set(h.needed_resources())
            for event in host.schedule:
                resources.update(event.command().needed_resources())

            def resolve_resource(r):
                if isinstance(r, str):
                    return Utils.resolve_resource_name(r)
                return r

            host.resources = set(map(resolve_resource, resources))

            ct.hosts[h['name']] = host

        ct.sanity_check()

        self._configured_test = ct

    def configured_test(self):
        return self._configured_test

