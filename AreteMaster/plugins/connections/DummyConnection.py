#!/usr/bin/env python
# coding=utf-8

from AreteMaster.controller.ConnectionPlugin import ConnectionPlugin
import os

class DummyConnection(ConnectionPlugin):
    connection_type = 'dummy'

    def __init__(self, host):
        self._host = host
        self._name = host.model['name']
        self._sent = 0
        self._connected = False

    def input(self):
        class DummyLine:
            def readline(s):
                if self._sent:
                    self._sent -= 1
                    ans = 'ok'
                    #print self._name+'< ', ans
                    return ans
                else:
                    e = IOError("dummy connection would block")
                    e.errno = os.errno.EAGAIN # i have no idea how to set it through constructor
                    raise e

        return DummyLine()

    def output(self):
        class decorator:
            def write(s, str):
                self._sent += 1
                print self._name+'> ', str,

        return decorator()

    def connected(self):
        return self._connected

    def connect(self):
        self._connected = True
        print self._name+'> ', ' -- connected --'

    def close(self):
        self._connected = False
        print self._name+'> ', ' -- disconnected --'

    def setblocking(self, blocking):
        self._blocking = blocking

