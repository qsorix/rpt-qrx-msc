#!/usr/bin/env python

import Model
import Network
import Mapping
import Schedule

class Configuration:
    def read(self, model, network, mapping, schedule):
        ctx_model = {}
        ctx_network = {}
        ctx_mapping = {}
        ctx_schedule = {}

        self.read_model(model, ctx_model)
        self.read_network(network, ctx_network)

        ctx_mapping.update(ctx_model)
        ctx_mapping.update(ctx_network)
        ctx_schedule.update(ctx_model)

        self.read_mapping(mapping, ctx_mapping)
        self.read_schedule(schedule, ctx_schedule)
    
    def read_model(self, model, ctx_local):
        ctx_global = Model.public_functions.copy()
        execfile(model, ctx_global, ctx_local)

    def read_network(self, network, ctx_local):
        ctx_global = Network.public_functions.copy()
        execfile(network, ctx_global, ctx_local)

    def read_mapping(self, mapping, ctx_local):
        ctx_global = Mapping.public_functions.copy()
        execfile(mapping, ctx_global, ctx_local)

    def read_schedule(self, schedule, ctx_local):
        ctx_global = Schedule.public_functions.copy()
        execfile(schedule, ctx_global, ctx_local)

