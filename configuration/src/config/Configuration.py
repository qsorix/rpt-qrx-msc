#!/usr/bin/env python

import Model
import Network
import Mapping
import Schedule
import Resources

class Host:
    def __init__(self):
        self.model = None
        self.network = None
        self.schedule = None
        self.resources = []

class ConfiguredTest:
    """
    Structure to easily pass test configuration.

    attributes:
        hosts - dictionary of Host objects (keys are names from
                Host.model.name()

        resources - dictionary of resources (keys are names from
                    resource.name()
    """
    pass

class Configuration:
    def __init__(self):
        self.__configured_test = []

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
            host = Host()
            host.model = h
            host.network = h.bound()
            host.schedule = Schedule.schedule.host_schedule(h.name())
            host.resources = h.needed_resources()

            ct.hosts[h.name()] = host

        self.__configured_test = ct

    def configured_test(self):
        return self.__configured_test

