#!/usr/bin/env python
# coding=utf-8

import os
import argparse
import shutil
import sys
from modules.Daemon import Daemon

try:
    import paramiko
    import base64
    has_ssh_support = True
except:
    has_ssh_support = False

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Main.py')
    
    parser.add_argument('-p', '--port', help="use port other than 4567", required=False, type=int, default=4567)
    parser.add_argument('-d', '--database', help="use database file other than 'aretes.db'", required=False, type=str, default='aretes.db')
    parser.add_argument('-l', '--log', help="use log file other than 'aretes.log'", required=False, type=str, default='aretes.log')
    parser.add_argument('-v', '--verbose', help="print everything to stderr too", required=False, action='store_true')
    parser.add_argument('-n', '--new', help="delete current database and log", required=False, action='store_true')
    parser.add_argument('-c', '--clean', help="delete temporary file directory", required=False, action='store_true')
    parser.add_argument('-s', '--ssh', help="use ssh to authorize connections", required=False, action='store_true', default=False)
    parser.add_argument('--authorized-keys', help="path to authorized keys file", required=False, type=str)
    parser.add_argument('--host-key', help="path to host's private key file", required=False, type=str)

    args = parser.parse_args()
 
    if args.clean:
        if os.path.isdir("./tmp"):
            shutil.rmtree("./tmp")
    if args.new:
        if os.path.isfile(args.database):
            os.remove(args.database)
        if os.path.isfile(args.log):
            os.remove(args.log)

    if args.ssh:
        if (not has_ssh_support):
            print >> sys.stderr, "In order to use ssh you must install paramiko library."
            sys.exit(1)

        if (args.authorized_keys is None) or (args.host_key is None):
            print >> sys.stderr, "In order to use ssh you must provide --authorized-keys and --host-key arguments"
            sys.exit(1)

        host_key = paramiko.RSAKey(filename=args.host_key)
        authorized_keys = load_authorized_keys(args.authorized_keys)
        daemon = Daemon(port=args.port, database=args.database, log=args.log, verbose=args.verbose, ssh=True, authorized_keys=authorized_keys, host_key=host_key)

    else:
        daemon = Daemon(port=args.port, database=args.database, log=args.log, verbose=args.verbose, ssh=False)

    daemon.run()
