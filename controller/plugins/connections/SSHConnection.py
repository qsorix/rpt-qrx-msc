#!/usr/bin/env python
# coding=utf-8

from common import Exceptions
from controller.ConnectionPlugin import ConnectionPlugin
import os
import stat

class SSHConnection(ConnectionPlugin):
    connection_type = 'ssh'
    needed_attributes = ['ip', 'connection_port', 'username' ]

    def __init__(self, host):
        try:
            import paramiko
        except:
            raise Exceptions.ConfigurationError("SSHConnection plugin needs paramiko library. Connection type 'ssh' will not be available.")

        self._ip = host.device['ip']
        self._port = host.device['connection_port']
        self._ssh = paramiko.SSHClient()
        self._channel = None

        self._username = host.device['username']

        if 'keyfile' in host.device:
            self._method='key'
            self._keyfile = host.device['keyfile']
            self._validate_key_file()

        elif 'password' in host.device:
            self._method='password'
            self._password = host.device['password']
        else:
            raise Exceptions.ConfigurationError("Required attribute not set for device {0}. SSHConnection plugin needs either 'keyfile' or 'password' attribute.".format(host.device['name']))

        self._ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

    def _validate_key_file(self):
        mode = os.stat(self._keyfile).st_mode
        # unwanted_bits = ----rwxrwx
        unwanted_bits = stat.S_IRWXG | stat.S_IRWXO
        if mode & unwanted_bits:
            raise Exceptions.ConfigurationError("Key file has wrong permissions. For security reasons group and other users cannot have any rights to this file.")

    def connected(self):
        return self._channel is not None

    def connect(self):
        if self._channel:
            # already connected
            return

        if self._method=='key':
            self._ssh.connect(self._ip, port=int(self._port), username=self._username, key_filename=self._keyfile)

        elif self._method=='password':
            self._ssh.connect(self._ip, port=self._port, username=self._username, password=self._password)

        self._channel = self._ssh.get_transport().open_session()

        self._in = self._channel.makefile('r', 0)
        self._out = self._channel.makefile('w', 0)

    def close(self):
        assert self._channel

        self._out.close()
        self._in.close()

        # paramiko is nasty and throws in close()
        try:
            self._channel.close()
        except:
            pass

        self._channel = None
        self._out = None
        self._in = None

    def input(self):
        assert self._in
        return self._in

    def output(self):
        assert self._out
        return self._out

    def setblocking(self, blocking):
        assert self._channel
        self._channel.setblocking(blocking)

