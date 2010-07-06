from FrontendPlugin import FrontendPlugin

class DaemonFrontend(FrontendPlugin):
    frontend_type = 'daemon'

    def deploy_configuration(self):
        # FIXME: probably move connection establishment to the controller so
        # frontends can be disconnected for the test period
        self.connect()

        host_commands = self.host().commands
        resources = self.host().resources

        out = self.output().write

        # FIXME: test id
        out('test @{id=FIXME}\n')

        for r in resources:
            r.transfer_with_daemon(self)

        for c in host_commands.check():
            out('check @{id=FIXME} ' + c + '\n')

        for c in host_commands.setup():
            out('setup @{id=FIXME} ' + c + '\n')

        for c in host_commands.cleanup():
            out('cleanup @{id=FIXME} ' + c + '\n')

        for c in host_commands.schedule():
            out('schedule @{id=%(id)s} @{run=%(run)s} %(cmd)s\n' %
                {'id': c.name(),
                 'run': c.run_policy().schedule_for_daemon(),
                 'cmd': c.command().command()})

        out('end\n')

    def start_sanity_check(self):
        self.output().write('start check\n')

    def wait_sanity_check(self):
        print '  -- waiting for sanity check to finish at ' + self.host().model.name() + ' --'
        resp = self.input().readline()
        #FIXME: check answer

    def start_test(self, timestamp):
        self.output().write('start test @{at=' + timestamp + '}\n')
        self.disconnect()

    def wait_test(self):
        print '  -- waiting for the test to finish at ' + self.host().model.name() + ' --'

    def fetch_results(self):
        self.connect()
        self.output().write('results @{id=FIXME}\n')
        self.disconnect()

    def foo():
        pass

