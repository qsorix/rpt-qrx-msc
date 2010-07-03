class HostCommands:
    def __init__(self):
        self.__setup    = []
        self.__schedule = []
        self.__cleanup  = []

    def add_setup(self, cmd):
        self.__setup.append(cmd)

    def add_cleanup(self, cmd):
        self.__cleanup.append(cmd)

    def add_schedule(self, cmd):
        self.__schedule.append(cmd)

    def dump(self):
        print self.__setup
        print self.__schedule
        print self.__cleanup

class DummyDriver:
    def process(self, cmd, host, attributes):
        for a in attributes:
            cmd.add_setup('setup ' + a)
            cmd.add_cleanup('cleanup ' + a)

            attributes.remove(a)

    def process_interface(self, cmd, host, interface, attributes):
        while attributes:
            a = attributes.pop()
            cmd.add_setup('setup dev ' + interface.bound().name() + '(' + interface.name() + ') ' + a)
            cmd.add_cleanup('cleanup dev ' + interface.bound().name() + ' ' + a)

    def process_event(self, cmd, host, event):
        cmd.add_schedule(event.command())
        return True

class Executer:
    def __init__(self):
        self.__host_drivers = [DummyDriver()]
        self.__interface_drivers = [DummyDriver()]
        self.__event_drivers = [DummyDriver()]

    def generate(self, host):
        cmd = HostCommands()

        attributes = host.model.attributes().keys()

        for d in self.__host_drivers:
            d.process(cmd, host, attributes)

        if attributes:
            print 'Unprocessed attributes: ', attributes

        for i in host.model.interfaces().values():
            self.generate_for_interface(cmd, host, i)

        for event in host.schedule:
            self.generate_for_event(cmd, host, event)

        return cmd

    def generate_for_event(self, cmd, host, event):
        processed = False

        for d in self.__event_drivers:
            if d.process_event(cmd, host, event):
                processed = True
                break

        if not processed:
            print 'Unprocessed event: ', event
    
    def generate_for_interface(self, cmd, host, interface):
        attributes = interface.attributes().keys()

        for d in self.__interface_drivers:
            d.process_interface(cmd, host, interface, attributes)

        if attributes:
            print 'Unprocessed interface attributes: ', attributes
