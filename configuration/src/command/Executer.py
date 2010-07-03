class HostCommands:
    def __init__(self):
        self.__check   = []
        self.__setup   = []
        self.__core    = []
        self.__cleanup = []

    def add_setup(self, cmd):
        self.__setup.append(cmd)

    def add_cleanup(self, cmd):
        self.__cleanup.append(cmd)

    def dump(self):
        print self.__check
        print self.__setup
        print self.__core
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

class Executer:
    def __init__(self):
        self.drivers = [DummyDriver()]
        self.interface_drivers = [DummyDriver()]

    def generate(self, host):
        cmd = HostCommands()

        attributes = host.model.attributes().keys()

        for d in self.drivers:
            d.process(cmd, host, attributes)

        if attributes:
            print 'Unprocessed attributes: ', attributes

        for i in host.model.interfaces().values():
            self.generate_for_interface(cmd, host, i)

        return cmd
    
    def generate_for_interface(self, cmd, host, interface):
        attributes = interface.attributes().keys()

        for d in self.interface_drivers:
            d.process_interface(cmd, host, interface, attributes)

        if attributes:
            print 'Unprocessed interface attributes: ', attributes
