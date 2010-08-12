#!/usr/bin/env python
# coding=utf-8

import nose
from nose.tools import with_setup
import socket
import os
import thread
import time

from daemon.Daemon import *
from daemon.Models import *

class TestDaemon:
    def _send_sth(self, sth):
        self.sock.send(sth)
        return self.sock.recv(1024).strip()

    @classmethod
    def setUpClass(self):
        setup_database()
        setup_config()

        def run_daemon():
            HOST, PORT = 'localhost', 9876
            SocketServer.TCPServer.allow_reuse_address = True
            daemon = SocketServer.TCPServer((HOST, PORT), DaemonHandler)
            daemon.serve_forever()

        self.daemon = thread.start_new_thread(run_daemon, ())
        time.sleep(0.3)

    def setUp(self):
        HOST, PORT = 'localhost', 9876
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

    def test_create_test_only(self):
        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('20')
        assert Test.get_by(id=u'test_daemon') != None

    def test_bad_line(self):
        reply = self._send_sth('bad line @{id=123}\n')
        assert reply.startswith('40')

    def test_create_and_delete_test(self):
        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('20')
        assert Test.get_by(id=u'test_daemon') != None

        reply = self._send_sth('end\n')
        assert reply.startswith('20')

#        reply = self._send_sth('delete @{id=test_daemon}\n')
#        assert reply.startswith('20')
#        assert Test.get_by(id=u'test_daemon') == None

    def test_same_id_commands(self):
        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('20')
        assert Test.get_by(id=u'test_daemon') != None

        reply = self._send_sth('setup @{id=setup} echo setup\n')
        assert reply.startswith('20')
        assert Setup.get_by(id=u'setup', test_id='test_daemon') != None

        reply = self._send_sth('check @{id=setup} echo wrong setup\n')
        assert reply.startswith('40')
        assert Setup.get_by(id=u'setup', test_id='test_daemon').command == 'echo setup'

    def test_create_two_tests_with_the_same_id(self):
        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('20')
        assert Test.get_by(id=u'test_daemon') != None

        reply = self._send_sth('end\n')
        assert reply.startswith('20')

        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('40')

    def test_create_full_test(self):
        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('20')
        assert Test.get_by(id=u'test_daemon') != None

        reply = self._send_sth('check @{id=check1} uname -a\n')
        assert reply.startswith('20')
        check = Check.get_by(id=u'check1')#, test_id='test_daemon')
        assert check != None
        assert check.command == 'uname -a'

        reply = self._send_sth('check @{id=check2} gcc --version\n')
        assert reply.startswith('20')
        check = Check.get_by(id=u'check2')#, test_id='test_daemon')
        assert check != None
        assert check.command == 'gcc --version'

        reply = self._send_sth('check @{id=check3} which badprogram\n')
        assert reply.startswith('20')
        check = Check.get_by(id=u'check3')#, test_id='test_daemon')
        assert check != None
        assert check.command == 'which badprogram'

        reply = self._send_sth('setup @{id=setup} echo setup\n')
        assert reply.startswith('20')
        setup = Setup.get_by(id=u'setup')#, test_id='test_daemon')
        assert setup != None
        assert setup.command == 'echo setup'

        reply = self._send_sth('task @{id=task} @{run=in 3} echo task\n')
        assert reply.startswith('20')
        task = Task.get_by(id=u'task')#, test_id='test_daemon')
        assert task != None
        assert task.command == 'echo task'
        assert task.run == 'in 3'

        reply = self._send_sth('end\n')
        assert reply.startswith('20')

    def test_send_file(self):
        reply = self._send_sth('test @{id=test_daemon}\n')
        assert reply.startswith('20')
        assert Test.get_by(id=u'test_daemon') != None

        self.sock.send('file @{id=file} @{size=3}\n')
        reply = self._send_sth('123')
        assert reply.startswith('20')
        file = File.get_by(id=u'file')#, test_id=u'test_daemon')
        assert file != None
        assert file.size == 3

        reply = self._send_sth('end\n')
        assert reply.startswith('20')

    def tearDown(self):
        self.sock.close()
        test = Test.get_by(id=u'test_daemon')
        if test:
            session.delete(test)
            session.commit()

