from config import Resources

class File(Resources.Resource):
    def __init__(self, name, path):
        self.rename(name)
        self.__path = path

    def __repr__(self):
        return 'File(%s)' % repr(self.path())

    def path(self):
        return self.__path

    def transfer_with_daemon(self, daemon):
        daemon.out().write('file ' + self.name() + ' <size> <content>')

