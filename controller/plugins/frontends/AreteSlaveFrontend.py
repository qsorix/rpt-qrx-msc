#!/usr/bin/env python
# coding=utf-8

from controller.FrontendPlugin import FrontendPlugin
from common import Database
from common import Exceptions

import datetime
import os

class _SentCommand:
    """Auxillary structure to store sent commands in uniform way."""

    def __init__(self, phase, type, value):
        self.phase = phase
        self.type = type
        self.value = value

class AreteSlaveFrontend(FrontendPlugin):
    frontend_type = 'arete_slave'

    def __init__(self, host, connection, configured_test):
        FrontendPlugin.__init__(self, host, connection, configured_test)
        self._sent_cmds = {}
        self._id = 0
        self._test_finished_flag = False

    def _make_id(self):
        while True:
            self._id += 1
            id = str('__auto__'+str(self._id))
            if id not in self._sent_cmds:
                return id

    def deploy_configuration(self):
        self.connect()

        host_commands = self.host().commands
        resources = self.host().resources

        def out(cmd):
            self.output().write(cmd)
            self._check_response();

        out('test @{id=%s}\n' % self.configuration().test_uuid)

        for r in resources:
            r.transfer_with_arete_slave(self)

        for c in host_commands.check():
            id = self._make_id()
            out('check @{id=%s} %s\n' % (id, c))

            assert id not in self._sent_cmds
            self._sent_cmds[id] = _SentCommand(phase='check', type='shell', value=c)

        for c in host_commands.setup():
            id = self._make_id()
            out('setup @{id=%s} %s\n' % (id, c))

            assert id not in self._sent_cmds
            self._sent_cmds[id] = _SentCommand(phase='setup', type='shell', value=c)

        for c in host_commands.cleanup():
            id = self._make_id()
            out('clean @{id=%s} %s\n' % (id, c))

            assert id not in self._sent_cmds
            self._sent_cmds[id] = _SentCommand(phase='cleanup', type='shell', value=c)

        for c in host_commands.schedule():
            out('task @{id=%(id)s} @{run=%(run)s} @{type=%(type)s} %(cmd)s\n' %
                {'id': c['name'],
                 'run': c.run_policy().schedule_for_arete_slave(),
                 'type': c.command().command_type(),
                 'cmd': c.command().command()})

            assert c['name'] not in self._sent_cmds
            self._sent_cmds[c['name']] = _SentCommand(phase='task', type=c.command().command_type(), value=c.command().command())

        out('end\n')

    def start_sanity_check(self):
        self._synchronize()

        self.output().write('prepare @{id=%s}\n' % self.configuration().test_uuid)

    def wait_sanity_check(self):
        print '  -- waiting for sanity check to finish at ' + self.host().model['name'] + ' --'
        resp = self.input().readline()

        if resp.startswith('200'):
            return

        if resp.startswith('401'):
            raise Exceptions.SlaveError('Sanity check failed on ' + self.host().model['name'])

        raise Exceptions.SlaveError('Unexpected result received after sanity check: ' + resp)

    def _synchronize(self):
        l1 = datetime.datetime.now()

        self.output().write('time\n')
        resp = self.input().readline()

        l2 = datetime.datetime.now()

        if not resp.startswith('200 OK '):
            raise Exceptions.SlaveError('Unable to synchronize, got response: ' + resp)

        r1 = datetime.datetime.strptime(resp.split()[2], '%Y-%m-%dT%H:%M:%S.%f')

        # assuming symmetric communication delay 0.5 * (l1-l2) is the point in
        # local when remote end is sending the response
        # it is written in a way it is because we can only subtract two time
        # values, and add two timedelta
        self._synchronization_offset = ((r1 - l1) + (r1 - l2)) // 2

    def start_test(self, duration_policy):
        self._duration_policy = duration_policy

        start = duration_policy.start()
        end = duration_policy.end_policy()

        start += self._synchronization_offset

        run = 'at ' + start.isoformat()

        self.output().write('start @{id=%s} @{run=%s} @{end=%s}\n' % (self.configuration().test_uuid, run, end))
        self._check_response();

        if self._disconnect_for_end_policy(end):
            self.disconnect()

    def trigger(self, trigger_name):
        if not self.connection().connected(): return

        self.output().write('trigger @{id=%s} @{name=%s}\n' % (self.configuration().test_uuid, trigger_name))

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
            return

        # Line in format: 100 Notify test_id trigger_name
        if line.startswith('100 Notify '):

            tokens = line.split()
            if len(tokens) == 4:
                trigger_name = line.split()[3]

                if trigger_name not in self.configuration().triggers:
                    raise RuntimeError("Received unknown trigger name ({0}).".format(trigger_name))

                self.configuration().triggers[trigger_name].notify()
                return

        raise RuntimeError("Not recognized message received from slave. Message is: {0}".format(line))

    def _disconnect_for_end_policy(self, end_policy):
        policy = self._duration_policy.end_policy().split()
        if policy[0] in ['duration']:
            return True

        if policy[0] in ['complete']:
            return False

        raise Exceptions.ConfigurationError("Unknown test end policy {0!r}".format(end_policy));

    def fetch_results(self):
        print '  -- fetching results from ' + self.host().model['name'] + ' --'

        self.connect()
        self.output().write('results @{id=%s}\n' % self.configuration().test_uuid)
        resp = self.input().readline()
        if resp.startswith('200'):
                       
            start_time = datetime.datetime.strptime(self._get_param('start_time')[0], '%Y-%m-%dT%H:%M:%S.%f')
            duration = datetime.timedelta(seconds=float(self._get_param('duration')[0]))
            
            node = Database.Node(test=Database.Test.get_by(id=unicode(self.configuration().test_uuid)), node=self.host().model['name'], start_time=start_time, duration=duration)

            for list in ['checks', 'setups', 'tasks', 'cleans']:
                ids = self._get_list(list)
                for id in ids:

                    c = self._sent_cmds[id]
                    if id not in self._sent_cmds:
                        raise Exceptions.SlaveError("Returned command ID {0} was not sent to slave.".format(id))

                    command = Database.Command(node=node, id=id, phase=c.phase, type=c.type, value=c.value)

                    start_times = map ((lambda x: datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f')), self._get_param('start_time', id))
                    durations = map ((lambda x: datetime.timedelta(seconds=float(x))), self._get_param('duration', id))
                    outputs = self._get_param('output', id)
                    returncodes = self._get_param('returncode', id)

                    invocations = len(start_times)
                    if (len(durations) != invocations or
                       len(outputs) != invocations or
                       len(returncodes) != invocations):
                        raise Exceptions.SlaveError("Protocol error. Mismatched number of values returned for invoked command.")

                    for i in range(invocations):
                        Database.Invocation(command=command, start_time=start_times[i], duration=durations[i], output=outputs[i], return_code=returncodes[i])

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
        if not reply.startswith('200'):
            raise Exceptions.SlaveError("Wrong response while receiving results")

        data_list = []
        sizes = reply.split(' ')[2:]
        for size in sizes:
            if size != 0:
                data = self.input().read(int(size))
            else:
                data = None
            data_list.append(data)
        return data_list

    def _check_response(self):
        resp = self.input().readline()
        if resp.startswith('200'):
            return

        raise Exceptions.SlaveError('Received wrong response. Expected 200 OK, got: ' + resp);
                    
    def abort_test(self):
        """If possible, abort the test.

        Do not throw exceptions."""

        try:
            if not self.connection().connected(): return

            self.output().write('stop @{id=%s}\n' % (self.configuration().test_uuid))
            self.disconnect()

        except Exception as e:
            print "Exception while aborting test. Ignoring: ", e

