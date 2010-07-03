#!/usr/bin/env python

import Model
import Network
import Mapping
import Schedule

class Host:
    def __init__(self):
        self.model = None
        self.network = None
        self.schedule = None

class Configuration:
    def __init__(self):
        self.__hosts = []

    def read(self, model, network, mapping, schedule):
        ctx_model = {}
        ctx_network = {}
        ctx_mapping = {}
        ctx_schedule = {}

        execfile(model, Model.public_functions.copy(), ctx_model)
        execfile(network, Network.public_functions.copy(), ctx_network)

        ctx_mapping.update(ctx_model)
        ctx_mapping.update(ctx_network)
        ctx_schedule.update(ctx_model)

        execfile(mapping, Mapping.public_functions.copy(), ctx_mapping)
        execfile(schedule, Schedule.public_functions.copy(), ctx_schedule)

        self.combine_hosts()
    
    def combine_hosts(self):
        for h in Model.model.hosts():
            host = Host()
            host.model = h
            host.network = h.bound()
            host.schedule = Schedule.schedule.host_schedule(h.name())

            self.hosts().append(host)

    def hosts(self): return self.__hosts;

