from config import Resources
from common import Exceptions

import os
import inspect

class File(Resources.Resource):
    def __init__(self, name, path):
        self.rename(name)

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
            frontend.output().write('file @{id=%(id)s} @{size=%(size)s}\n' % {'id':self['name'], 'size':self._size})
            frontend.output().write(file.read())

            resp = frontend.input().readline().strip()
            if resp != 'ok':
                raise RuntimeError('Wrong response while transfering file')


# FIXME: just a test of generate_commands. not production ready
class TarBall(File):
    def generate_commands(self, cmd, host):
        cmd.add_check('which tar')
        cmd.add_setup('tar zxf @{' + self['name'] + '.path}')
