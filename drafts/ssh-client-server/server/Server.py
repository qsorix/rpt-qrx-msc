#!/usr/bin/env python
# coding=utf-8

import sys
import SocketServer
import paramiko
import base64

def load_authorized_keys(filename):
    #FIXME: ssh sprawdza prawa i odmowia pracy, jesli plik authorized_keys ma
    # inne prawa niz 0400. To dobry pomysl jest :)
    #
    # poza tym wypadaloby moze te funkcje troche bardziej 'bledo-odpornie'
    # napisac, teraz sie pewnie ostro sypnie jak w pliku beda jakies krzaki
    with open(filename, 'r') as f:
        lines = f.readlines()

        # wez druga kolumne z wszystkich linii, zdedokuj i zrob z niej klucze
        return map(lambda x: paramiko.RSAKey(data=base64.decodestring(x.split()[1])), lines)

# prywatny klucz serwera
host_key = paramiko.RSAKey(filename='ssh_host_rsa_key')

# publiczne klucze userow
authorized_keys = load_authorized_keys(filename='authorized_keys')

class SSHServer (paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        print 'auth attempt with passwd, from', username, 'password', password
        if username=='guest' and password=='dupa':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print 'auth attempt with key'
        if key in authorized_keys:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        print 'channel request', kind, chanid
        if kind=='session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return 'pubkey,password'

class SSHConnectionHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        transport = paramiko.Transport(self.request)
        transport.add_server_key(host_key)
        transport.start_server(server=SSHServer())

        # to akceptuje 'channel' w obrebie polaczenia. na jednym polaczeniu ssh
        # moze byc otwartych kilka kanalow. np. jeden z terminalem, inny z sftp
        # a ja tu oczekuje, ze user poprosil o channel typu 'session', gdzie
        # sobie bedziemy robic wejscie/wyjscie
        channel = transport.accept()

        # channel ma interfejs jak socket
        cin = channel.makefile('r', 0)
        cout = channel.makefile('w', 0)

        cout.write('foo\n')
        print cin.readline()
        cout.write('wassup\n')

        print 'end of communication'

        try:
            # sometimes raise EOFError -- seems like a bug
            channel.close()
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "Usage: {0} <ip> <port>".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    server = SocketServer.TCPServer((ip, port), SSHConnectionHandler)

    server.serve_forever()
