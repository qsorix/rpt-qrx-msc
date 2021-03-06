#!/usr/bin/env python
# coding=utf-8

import DriverPlugin

class PreparedCommands(dict):
    """
    Datatype to hold Generator.process() result.

    Keys are model hosts' names, values are instances of HostCommands class.
    """
    pass

import re

class HostCommands:
    def __init__(self):
        self._check    = [] # list of strings
        self._setup    = [] # list of strings
        self._schedule = [] # list of Schedule.Event
        self._cleanup  = [] # list of strings

    def add_check(self, cmd):
        self._check.append(cmd)

    def add_check_unique(self, cmd):
        if cmd not in self._check:
            self.add_check(cmd)

    def add_setup(self, cmd):
        self._setup.append(cmd)

    def add_cleanup(self, cmd):
        self._cleanup.append(cmd)

    def add_schedule(self, cmd):
        self._schedule.append(cmd)

    def check(self): return self._check
    def setup(self): return self._setup
    def schedule(self): return self._schedule
    def cleanup(self): return self._cleanup

    def accept_transformation(self, transformation):
        """
        Runs transformation on all command strings and stores the returned
        values instead.
        """
        self._check = map(transformation, self._check)
        self._setup = map(transformation, self._setup)
        self._cleanup = map(transformation, self._cleanup)

        for event in self.schedule():
            event.command().accept_transformation(transformation)

class Generator:
    def __init__(self):
        self._host_drivers = [x() for x in DriverPlugin.HostDriverPlugin.plugins]
        self._interface_drivers = [x() for x in DriverPlugin.InterfaceDriverPlugin.plugins]

    def process(self, configured_test):
        result = PreparedCommands()

        for host in configured_test.hosts.values():
            result[host.model['name']] = self._generate(host)

        self._perform_substitutions(result, configured_test)

        for (host, commands) in result.items():
            configured_test.hosts[host].commands = commands

        return result

    def _generate(self, host):
        cmd = HostCommands()

        attributes = host.model.attributes()
        attributes.remove('name')

        for d in self._host_drivers:
            d.process(cmd, host, attributes)

        if attributes:
            print 'Unprocessed attributes: ', attributes

        for i in host.model.interfaces().values():
            self._generate_for_interface(cmd, host, i)

        for event in host.schedule:
            self._generate_for_event(cmd, host, event)

        for resource in host.resources:
            self._generate_for_resource(cmd, host, resource)

        return cmd

    def _generate_for_resource(self, cmd, host, resource):
        resource.generate_commands(cmd, host)

    def _generate_for_event(self, cmd, host, event):
        for s in event.command().sanity_checks():
            cmd.add_check_unique(s)

        cmd.add_schedule(event)
    
    def _generate_for_interface(self, cmd, host, interface):
        attributes = interface.attributes()
        attributes.remove('name')

        for d in self._interface_drivers:
            d.process_interface(cmd, host, interface, attributes)

        if attributes:
            print 'Unprocessed interface attributes: ', attributes

    def _perform_substitutions(self, prepared_commands, configured_test):
        for host, commands in prepared_commands.items():

            substitution = lambda x: self._substitute_for_host(host, x, configured_test)

            commands.accept_transformation(substitution)

    def _substitute_for_host(self, host, command, configured_test):
        models = dict([(h.model['name'], h.model) for h in configured_test.hosts.values()])

        def resovle_ref(matchobj):
            ref = matchobj.group('ref').split('.')

            if len(ref) > 1 and ref[0] in models:
                host = models[ref.pop(0)]
                if ref[0] in host.interfaces() and len(ref) > 1:
                    interface = host.interface(ref.pop(0))

                    if len(ref) == 1:
                        if ref[0] != 'name' and ref[0] in interface.attributes():
                            return interface[ref[0]]

                        if ref[0] in interface.bound().attributes():
                            return interface.bound()[ref[0]]

                else:
                    if len(ref) == 1:
                        if ref[0] != 'name' and ref[0] in host.attributes():
                            return host[ref[0]]

                        if ref[0] in host.bound().attributes():
                            return host.bound()[ref[0]]

            else:
                #FIXME: warn/error ?
                pass

            return '@{' + matchobj.group('ref') + '}'

        return re.sub('@{(?P<ref>[a-zA-Z0-9\._]+)}', resovle_ref, command)
