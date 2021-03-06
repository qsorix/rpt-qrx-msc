#!/usr/bin/env python
# coding=utf-8

from config import Resources
from common import Exceptions

import os
import inspect

class File(Resources.Resource):
    """
    Constructs resource representing specified *id*

    :param id: id for this resource
    :param path: path of the file
    :param name: name for this resource
    :param chmod: if passed, chmod will be called with given value
    """
    def __init__(self, id, path, name=None, chmod=None):
        self.rename(id)
        if name is None:
            self._name = os.path.basename(path)
        else:
            self._name = name
        self._chmod = chmod

        try:
            self._stat_path(path)

        except OSError as e:
            if e.errno == os.errno.ENOENT:
                try:
                    calling_file = inspect.stack()[1][1]
                    relpath = os.path.join(os.path.dirname(calling_file), path)
                    self._stat_path(relpath)

                except OSError as e:
                    if e.errno == os.errno.ENOENT:
                        raise Exceptions.ConfigurationError("Could not locate file '{0}'.".format(path))
                    else:
                        raise e
            else:
                raise e

    def _stat_path(self, path):
        stat = os.stat(path)
        self._path = path
        self._size = stat.st_size

    def __repr__(self):
        return 'File(%s)' % repr(self.path())

    def path(self):
        return self._path

    def transfer_with_arete_slave(self, frontend):
        with open(self._path, 'rb') as file:
            frontend.output().write('file @{id=%(id)s} @{size=%(size)s} @{name=%(name)s}\n' \
                % {'id':self['name'], 'size':self._size, 'name':self._name})
            try:
                while True:
                    READ_SIZE = 1000000
                    data = file.read(READ_SIZE)
                    frontend.output().write(data)
                    if len(data) < READ_SIZE:
                        break
            except Exception as E:
                print type(E), E

            resp = frontend.input().readline().strip()
            if not resp.startswith('200'):
                raise RuntimeError('Wrong response while transfering file. Expected 200 OK, got \'' + resp + '\'')

    def generate_commands(self, cmd, host):
        """
        If chmod was set, will call chmod
        """
        if self._chmod:
            cmd.add_check_unique('which chmod')
            cmd.add_setup('chmod ' + self._chmod + ' @{' + self['name'] + '.name}')

# FIXME: just a test of generate_commands. not production ready
class TarBall(File):
    def generate_commands(self, cmd, host):
        cmd.add_check('which tar')
        cmd.add_setup('tar zxf @{' + self['name'] + '.path}')
