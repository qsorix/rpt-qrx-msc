from controller.FrontendPlugin import FrontendPlugin

import time

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
        # TODO It's yours. I don't know what you mean.
        out('test @{id=%s}\n' % self._test_id)
        resp = self.input().readline()

        for r in resources:
            r.transfer_with_daemon(self)

        for c in host_commands.check():
            id = self._make_id()
            out('check @{id=%i} %s\n' % (id, c))
            resp = self.input().readline()
            assert id not in self._sent_cmds
            self._sent_cmds[id] = c

        for c in host_commands.setup():
            id = self._make_id()
            out('setup @{id=%i} %s\n' % (id, c))
            resp = self.input().readline()
            assert id not in self._sent_cmds
            self._sent_cmds[id] = c

        for c in host_commands.cleanup():
            id = self._make_id()
            out('clean @{id=%i} %s\n' % (id, c))
            resp = self.input().readline()
            assert id not in self._sent_cmds
            self._sent_cmds[id] = c

        for c in host_commands.schedule():
            out('task @{id=%(id)s} @{run=%(run)s} %(cmd)s\n' %
                {'id': c['name'],
                 'run': c.run_policy().schedule_for_daemon(),
                 'cmd': c.command().command()})
            resp = self.input().readline()
            assert c['name'] not in self._sent_cmds
            self._sent_cmds[c['name']] = c

        out('end\n')
        resp = self.input().readline()

    def start_sanity_check(self):
        self.output().write('prepare @{id=%s}\n' % self._test_id)

    def wait_sanity_check(self):
        print '  -- waiting for sanity check to finish at ' + self.host().model['name'] + ' --'
        resp = self.input().readline()
        if resp.startswith('401'):
            print 'sanity check failed'
            # TODO Do sth about it

    def start_test(self, timestamp):
        # FIXME Fix the whole run/end/timestamp thing.
        run = 'in 2'
        end = 'duration 3'
        self.output().write('start @{id=%s} @{run=%s} @{end=%s}\n' % (self._test_id, run, end))
        resp = self.input().readline()
        self.disconnect()

    def wait_test(self):
        print '  -- waiting for the test to finish at ' + self.host().model['name'] + ' --'

        # FIXME It should wait for 'duration' + 1 seconds unless in some other mode.
        end = 'duration 3'
        wait_time = int(end.split(' ')[1])
        time.sleep(wait_time)

    def fetch_results(self):
        self.connect()

        self.output().write('results @{id=%s}\n' % self._test_id)
        resp = self.input().readline()
        for id in self._sent_cmds.keys():
            self.output().write('get @{id=%s}\n' % id)

            # FIXME Put those results in some database or sth.
            reply = self.input().readline()

            if reply.startswith('20'):
                size = int(reply.split(' ')[2])

                received = 0
                while received + 1024 < size:
                    data = self.input().read(1024)
                    received += 1024
                    print data
                data = self.input().read(size)
                print data

        self.output().write('end\n')
        resp = self.input().readline()

        # FIXME Temporarily deleting test after fetching results.
        self.output().write('delete @{id=%s}\n' % self._test_id)
        resp = self.input().readline()

        self.disconnect()

    def abort_test(self):
        # TODO Implement aborting sanity check and test itself.
        pass
