#!/usr/bin/env python

import Model
import Network
import Mapping
import Schedule
import Resources
import common.Exceptions

class ConfiguredHost:
    def __init__(self):
        self.model = None
        self.network = None
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
        for (name, host) in self.hosts.items():
            if name != host.model.name():
                raise Exceptions.SanityError("Key name is different than element's name")

            if not host.model.bound():
                raise Exceptions.SanityError("Model host '%s' is not bound" % host.name())

            network = host.network

            if 'connection' not in network.attributes():
                raise Exceptions.SanityError("Network host '%s' doesn't specify connection attribute" % network.name())

            for (iname, interface) in host.model.interfaces().items():
                if iname != interface.name():
                    raise Exceptions.SanityError("Key's name is different than element's name")

                if not interface.bound():
                    raise Exceptions.SanityError("Interface '%s' of host '%s' is not bound" % (iname, name))

class Configuration:
    def __init__(self):
        self._configured_test = []

    def read(self, model, network, mapping, schedule):
        # local variables for each configuration file
        ctx_model = {}
        ctx_network = {}
        ctx_mapping = {}
        ctx_schedule = {}

        # resources can be defined in any configuration part
        glob_resources = Resources.public_functions
        def setup_glob(module):
            x = module.public_functions.copy()
            x.update(glob_resources)
            return x

        (glob_model, glob_network, glob_mapping, glob_schedule) = map(setup_glob, [Model, Network, Mapping, Schedule])

        execfile(model, glob_model, ctx_model)
        execfile(network, glob_network, ctx_network)

        # populate mapping and schedule with variables defined in model/network parts
        ctx_mapping.update(ctx_model)
        ctx_mapping.update(ctx_network)

        ctx_schedule.update(ctx_model)

        execfile(mapping, glob_mapping, ctx_mapping)
        execfile(schedule, glob_schedule, ctx_schedule)

        self.combine_hosts()

        return self.configured_test()
    
    def combine_hosts(self):
        ct = ConfiguredTest()
        ct.resources = Resources.resources.resources()
        ct.hosts = {}

        for h in Model.model.hosts():
            host = ConfiguredHost()
            host.model = h
            host.network = h.bound()
            host.schedule = Schedule.schedule.host_schedule(h.name())
            host.resources = set(h.needed_resources())
            for event in host.schedule:
                host.resources.update(event.command().needed_resources())

            ct.hosts[h.name()] = host

        self._configured_test = ct

    def configured_test(self):
        return self._configured_test

