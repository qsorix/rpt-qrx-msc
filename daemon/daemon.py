#!/usr/bin/env python
# coding=utf-8

import sys
from scheduler import TaskScheduler
from test import Task, Test
import re
from time import strptime
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True

class DaemonHandler(SocketServer.StreamRequestHandler):

    def send(self, msg):
        print >> sys.stderr, "[%s] Sending: %s" % (self.client_address[0], msg)
        self.wfile.write(msg)

    def send_ok(self):
        self.send('200 OK\n')

    def send_bad_request(self):
        self.send('400 Bad Request\n')

    def send_end(self):
        self.send('600 The End\n')

    def receive(self):
        data = self.rfile.readline().strip()
        if data:
            print >> sys.stderr, "[%s] Received: %s" % (self.client_address[0], data)
        return data

    def handle(self):
        line = self.receive()

        if re.search('^test [0-9]+$', line):
            self.send_ok()
            self.recv_test(int(line[5:]))
        elif re.search('^results [0-9]+$', line):
            self.send_ok()
            self.send_results(int(line[8:]))

    def send_results(self, test_nr):
        test = self.daemon.tests.get(test_nr)
    
        print 'Sending results for test', test_nr

        for task in test.results_tasks:
            self.send(test.results_tasks.get(task)+'\n')

        for cmd in test.results_cmds:
            self.send(test.results_cmds.get(cmd)+'\n')

    def recv_test(self, test_nr):
        test = Test(test_nr)

        line = self.receive()
        while not re.search('^end$', line):
            if re.search('^file \{.+\} [0-9]+$', line):
                test.files[line.split(' ')[1][1:-1]] = self.receive()
                self.send_ok()

            elif re.search('^schedule [0-9]+$', line):
                test.tasks = []
                self.send_ok()

                for i in range(0, int(line.split(' ')[1])):
                    task_line = self.receive()

                    if not re.search('^[0-9]+\: .+$', task_line):
                        self.send_bad_request()
                        return

                    task = task_line.split(':')
                    test.tasks.append(Task(int(task[0]), task[1][1:]))

                    self.send_ok()

            elif re.search('^cmds [0-9]+$', line):
                test.cmds = []
                self.send_ok()

                for i in range(0, int(line.split(' ')[1])):
                    cmd_line = self.receive()

                    if not re.search('^[0-9]+\: .+$', cmd_line):
                        self.send_bad_request()
                        return

                    cmd = cmd_line.split(':')
                    test.cmds.append(Task(int(cmd[0]), cmd[1][1:]))

                    self.send_ok()

            elif re.search('^start [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$', line):
                test.start = strptime(line[6:], "%Y-%m-%d %H:%M:%S")

                self.send_ok()

            elif re.search('^duration [0-9]+$', line):
                test.duration = int(line[9:])

                self.send_ok()

            else:
                self.send_bad_request()
                return

            line = self.receive()

        self.send_end()

        print test

        errors = test.check()
        if errors == None:
            self.daemon.tests[test.id] = test
            ts = TaskScheduler(test)
#            ts.run()
        else:
            print 'Test %d is not valid because:' % test.id
            for error in errors:
                print ' - %s' % error

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    daemon = SocketServer.TCPServer((HOST, PORT), DaemonHandler)
    daemon.serve_forever()
