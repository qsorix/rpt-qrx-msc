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
        #FIXME: send proper size and file's content
        daemon.output().write('file @{id=%(id)s} @{size=%(size)s}\n' % {'id':self['name'], 'size':0})
        resp = daemon.input().readline().strip()
        if resp != 'ok':
            raise RuntimeError('Wrong response while transfering file')

