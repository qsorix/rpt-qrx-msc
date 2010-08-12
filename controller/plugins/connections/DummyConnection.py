from controller.ConnectionPlugin import ConnectionPlugin

class DummyConnection(ConnectionPlugin):
    connection_type = 'dummy'

    def __init__(self, host):
        self._host = host
        self._name = host.model['name']

    def input(self):
        class DummyLine:
            def readline(s):
                ans = 'ok'
                #print self._name+'< ', ans
                return ans

        return DummyLine()

    def output(self):
        class decorator:
            def write(s, str):
                print self._name+'> ', str,

        return decorator()

    def connect(self):
        print self._name+'> ', ' -- connected --'

    def close(self):
        print self._name+'> ', ' -- disconnected --'

