from controller.FrontendPlugin import FrontendPlugin

import datetime
import os

class DaemonFrontend(FrontendPlugin):
    frontend_type = 'daemon'

    def __init__(self, host, connection, test_uuid):
        FrontendPlugin.__init__(self, host, connection)
        self._sent_cmds = {}
        self._id = 0
        self._test_id = test_uuid
        self._test_finished_flag = False

    def _make_id(self):
        self._id += 1
        return self._id

    def deploy_configuration(self):
        self.connect()

        host_commands = self.host().commands
        resources = self.host().resources

        out = self.output().write

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

    def start_test(self, duration_policy):
        self._duration_policy = duration_policy

        start = duration_policy.start()
        end = duration_policy.end_policy()

        # TODO From start time (local) and time offset acquired during
        # synchronization calculate remote time at which test should start
        # start += synchronizated_offset

        run = 'at ' + start.isoformat()

        self.output().write('start @{id=%s} @{run=%s} @{end=%s}\n' % (self._test_id, run, end))
        resp = self.input().readline()

        if self._disconnect_for_end_policy(end):
            self.disconnect()

    def check_test_end(self):
        self._non_blocking_io()
        return self._test_end()

    def _non_blocking_io(self):
        conn = self.connection()

        if not conn.connected(): return
        if not hasattr(conn, 'setblocking'): return

        try:
            conn.setblocking(False)
            while True:
                line = conn.input().readline()
                self._async_input(line)

        except IOError as e:
            if e.errno not in [os.errno.EAGAIN, os.errno.EWOULDBLOCK]:
                raise

        finally:
            conn.setblocking(True)

    def _test_end(self):
        print '  -- waiting for the test to finish at ' + self.host().model['name'] + ' --'

        policy = self._duration_policy.end_policy().split()
        if policy[0] == 'duration':
            duration = datetime.timedelta(seconds=float(policy[1]))
            start = self._duration_policy.start()
            end   = start + duration
            now   = datetime.datetime.now()

            def total_seconds(td):
                return (td.microseconds + (td.seconds + td.days *  24 * 3600) * 10**6) / 10**6

            # True if past end time
            return (total_seconds(end - now) < 0)

        if policy[0] == 'complete':
            return self._test_finished_flag

    def _async_input(self, line):
        line = line.strip()
        print '  -- received {0} at {1} -- '.format(line, self.host().model['name'])
        if line == '100 Test Finished':
            self._test_finished_flag = True

    def _disconnect_for_end_policy(self, end_policy):
        policy = self._duration_policy.end_policy().split()
        if policy[0] in ['duration']:
            return True

        if policy[0] in ['complete']:
            return False

        raise ConfigurationError("Unknown test end policy {0!r}".format(end_policy));

    def fetch_results(self):
        self.connect()

        self.output().write('results @{id=%s}\n' % self._test_id)
        resp = self.input().readline()
        if resp.startswith('20'):

            # FIXME Put those results in some database or sth.
            started_at = self._get_param('started_at')
            duration = self._get_param('duration')
            print 'test', self._test_id, ':', started_at, duration

            for list in ['checks', 'setups', 'tasks', 'cleans']:
                ids = self._get_list(list)
                print list, ':'
                for id in ids:
                    returncode = self._get_param('returncode', id)
                    output = self._get_param('output', id)
                    started_at = self._get_param('started_at', id)
                    duration = self._get_param('duration', id)
                    print id, ':', returncode, output, started_at, duration
               
            self.output().write('end\n')
            resp = self.input().readline()

        self.disconnect()

    def _get_list(self, list_name):
         self.output().write('get @{%s}\n' % (list_name))
         reply = self.input().readline().strip()
         if reply.startswith('201'):
            ids = reply.split(' ')[2:]
            return ids

    def _get_param(self, param, task_id=None):
        if task_id:
            self.output().write('get @{%s.%s}\n' % (task_id, param))
        else:
            self.output().write('get @{%s}\n' % (param))
        reply = self.input().readline().strip()
        if reply.startswith('200'):
            sizes = reply.split(' ')[2:]
            for size in sizes:
                data = self.input().read(int(size)).strip()
                return data
                print data
                    
    def abort_test(self):
        # TODO Implement aborting sanity check and test itself.
        pass
