#!/usr/bin/env python

import sys
import paramiko

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "Usage: {0} <ip> <port>".format(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    ssh = paramiko.SSHClient()

    # krzyczy, ze nie zna hosta. w sumie mozna tez ignorowac (inna Policy)... i
    # tak nie chce nam sie implementowac jeszcze listy znanych hostow
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

    # autoryzacja haslem lub kluczem. user do klucza nie jest wymagany

    # ssh.connect(ip, port=port, username='guest', password='dupa')
    ssh.connect(ip, port=port, username='guest', key_filename='id_rsa')

    # session ma interfejs jak socket
    session = ssh.get_transport().open_session()

    # wiec mozna sobie zrobic pliki do czytania/pisania
    cin = session.makefile('r', 0)
    cout = session.makefile('w', 0)

    print cin.readline()
    cout.write('hello\n')
    print cin.readline()

    print 'end of communication'

    # paramiko tu rzuca wyjatkami, fail...
    try:
        session.close()
    except:
        pass

    try:
        ssh.close()
    except:
        pass


