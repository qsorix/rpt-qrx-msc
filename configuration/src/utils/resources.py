from config import Resources

class File(Resources.Resource):
    def __init__(self, name, path):
        self.rename(name)
        self._path = path

    def __repr__(self):
        return 'File(%s)' % repr(self.path())

    def path(self):
        return self._path

    def transfer_with_daemon(self, daemon):
        daemon.connection().output().write('file ' + self.name() + ' <size> <content>\n')
        resp = daemon.connection().input().readline()
        if resp.split()[0] != '200':
            raise RuntimeError('Wrong response while transfering file')

