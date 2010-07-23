#!/usr/bin/env python
# coding=utf-8

import py
import socket
from daemon.daemon import *
from daemon.models import *
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

def test_create_test_123_only():
#    thread.start_new_thread(run_daemon, (5001,))
    sock = connect_to_daemon(9999)

    sock.send('test @{id=123}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    # TODO Test if it was created

    sock.send('close\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('60')
    sock.close()

def test_bad_line():
#    thread.start_new_thread(run_daemon, (5002,))
    sock = connect_to_daemon(9999)

    sock.send('bad line @{id=123}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('40')

    sock.send('close\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('60')
    sock.close()

def test_delete_test_123():
    sock = connect_to_daemon(9999)

    sock.send('delete @{id=123}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    #assert Test.get_by(id='123') == None
    # TODO Test if it was deleted

    sock.send('close\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('60')
    sock.close()

def test_create_full_test():
    sock = connect_to_daemon(9999)

    sock.send('test @{id=666}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('check @{id=check1} @{command=uname -a}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('check @{id=check2} @{command=gcc --version}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('setup @{id=setup} @{command=echo \'setup\'}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('setup @{id=setup} @{command=echo \'correct setup\'}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('20')

    sock.send('check @{id=setup} @{command=echo \'wrong setup\'}\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('40')

    sock.send('close\n')
    reply = sock.recv(1024).strip()
    assert reply.startswith('60')
    sock.close()

 
