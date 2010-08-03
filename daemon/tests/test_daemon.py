#!/usr/bin/env python
# coding=utf-8

import py
import socket
import os
from daemon.Daemon import *
from daemon.Models import *
import thread
import time

def run_daemon(port):
    setup_database()
    setup_config()

    HOST, PORT = "localhost", port
    SocketServer.TCPServer.allow_reuse_address = True
    daemon = SocketServer.TCPServer((HOST, PORT), DaemonHandler)
    daemon.serve_forever()

def connect_to_daemon(port):
    time.sleep(0.5)

    HOST, PORT = "localhost", port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    return sock

def test_create_test_only():
#    thread.start_new_thread(run_daemon, (5001,))
    sock = connect_to_daemon(9999)

    sock.send('test @{id=123}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    # TODO Test if it was created

    sock.close()

def test_bad_line():
#    thread.start_new_thread(run_daemon, (5002,))
    sock = connect_to_daemon(9999)

    sock.send('bad line @{id=123}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('40')

    sock.close()

def test_delete_test_123():
    sock = connect_to_daemon(9999)

    sock.send('delete @{id=123}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    #assert Test.get_by(id='123') == None
    # TODO Test if it was deleted

    sock.close()

def test_same_id_commands():
    sock = connect_to_daemon(9999)

    sock.send('test @{id=512}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('setup @{id=setup} echo \'setup\'\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('setup @{id=setup} echo \'correct setup\'\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('40')

    sock.send('check @{id=setup} echo \'wrong setup\'\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('40')

    sock.close()

def test_create_two_tests_with_the_same_id():
    sock = connect_to_daemon(9999)

    sock.send('test @{id=356}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('end\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('test @{id=356}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('40')

    sock.close()

def test_create_full_test():
    sock = connect_to_daemon(9999)

    sock.send('test @{id=666}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('check @{id=check1} uname -a\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('check @{id=check2} gcc --version\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('setup @{id=setup} echo \'setup\'\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('end\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.close()


