import DriverPlugin

class PreparedCommands(dict):
    """
    Datatype to hold Generator.process() result.

    Keys are model hosts' names, values are instances of HostCommands class.
    """
    pass

class HostCommands:
    def __init__(self):
        self._check    = [] # list of strings
        self._setup    = [] # list of strings
        self._schedule = [] # list of Schedule.Event
        self._cleanup  = [] # list of strings

    def add_check(self, cmd):
        self._check.append(cmd)

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

class Generator:
    def __init__(self):
        self._host_drivers = [x() for x in DriverPlugin.HostDriverPlugin.plugins]
        self._interface_drivers = [x() for x in DriverPlugin.InterfaceDriverPlugin.plugins]

    def process(self, configured_test):
        result = PreparedCommands()

        for host in configured_test.hosts.values():
            result[host.model['name']] = self._generate(host)

        return result

    def _generate(self, host):
        cmd = HostCommands()

        attributes = host.model.attributes()

        for d in self._host_drivers:
            d.process(cmd, host, attributes)

        if attributes:
            print 'Unprocessed attributes: ', attributes

        for i in host.model.interfaces().values():
            self._generate_for_interface(cmd, host, i)

        for event in host.schedule:
            self._generate_for_event(cmd, host, event)

        return cmd

    def _generate_for_event(self, cmd, host, event):
        for s in event.command().sanity_checks():
            cmd.add_check(s)

        cmd.add_schedule(event)
    
    def _generate_for_interface(self, cmd, host, interface):
        attributes = interface.attributes()

        for d in self._interface_drivers:
            d.process_interface(cmd, host, interface, attributes)

        if attributes:
            print 'Unprocessed interface attributes: ', attributes
