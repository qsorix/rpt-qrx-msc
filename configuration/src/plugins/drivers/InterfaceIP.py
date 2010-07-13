from command.DriverPlugin import InterfaceDriverPlugin

class InterfaceIP(InterfaceDriverPlugin):
    def process_interface(self, cmd, host, interface, attributes):
        if 'ip' not in attributes:
            return

        ip = interface['ip']
        cmd.add_check('which ip')

        args = {'ip': interface['ip'],
                'dev': interface.bound()['name']}
        cmd.add_setup('ip addr add %(ip)s dev %(dev)s' % args)
        cmd.add_cleanup('ip addr del %(ip)s dev %(dev)s' % args)

        attributes.remove('ip')
