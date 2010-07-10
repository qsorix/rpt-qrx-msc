from controller.FrontendPlugin import FrontendPlugin

class DaemonFrontend(FrontendPlugin):
    frontend_type = 'daemon'

    def __init__(self, host, connection, test_uuid):
        FrontendPlugin.__init__(self, host, connection)
        self._sent_cmds = {}
        self._id = 0
        self._test_id = test_uuid

    def _make_id(self):
        self._id += 1
        return self._id

    def deploy_configuration(self):
        self.connect()

        host_commands = self.host().commands
        resources = self.host().resources

        out = self.output().write

        # FIXME: test id
        out('test @{id=%s}\n' % self._test_id)

        for r in resources:
            r.transfer_with_daemon(self)

        for c in host_commands.check():
            id = self._make_id()
            out('check @{id=%i} %s\n' % (id, c))
            assert id not in self._sent_cmds
            self._sent_cmds[id] = c

        for c in host_commands.setup():
            id = self._make_id()
            out('setup @{id=%i} %s\n' % (id, c))
            assert id not in self._sent_cmds
            self._sent_cmds[id] = c

        for c in host_commands.cleanup():
            id = self._make_id()
            out('cleanup @{id=%i} %s\n' % (id, c))
            assert id not in self._sent_cmds
            self._sent_cmds[id] = c

        for c in host_commands.schedule():
            out('schedule @{id=%(id)s} @{run=%(run)s} %(cmd)s\n' %
                {'id': c.name(),
                 'run': c.run_policy().schedule_for_daemon(),
                 'cmd': c.command().command()})
            assert c.name() not in self._sent_cmds
            self._sent_cmds[c.name()] = c

        out('end\n')

    def start_sanity_check(self):
        self.output().write('start check @{id=%s}\n' % self._test_id)

    def wait_sanity_check(self):
        print '  -- waiting for sanity check to finish at ' + self.host().model.name() + ' --'
        resp = self.input().readline()
        #FIXME: check answer

    def start_test(self, timestamp):
        self.output().write('start test @{id=%s} @{at=%s}\n' % (self._test_id, timestamp))
        self.disconnect()

    def wait_test(self):
        print '  -- waiting for the test to finish at ' + self.host().model.name() + ' --'

    def fetch_results(self):
        self.connect()

        #FIXME: protocol z dupy
        self.output().write('results @{id=%s}\n' % self._test_id)
        for id in self._sent_cmds.keys():
            self.output().write('get ' + str(id) + '\n')
        self.output().write('end\n')
        self.disconnect()
