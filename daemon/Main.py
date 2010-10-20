#!/usr/bin/env python
# coding=utf-8

import sys
import os
import argparse
import shutil
from modules.Daemon import Daemon

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Main.py')
    
    parser.add_argument('-p', '--port', help="use port other than 4567", required=False, type=int, default=4567)
    parser.add_argument('-d', '--database', help="use database file other than 'aretes.db'", required=False, type=str, default='aretes.db')
    parser.add_argument('-l', '--log', help="use log file other than 'aretes.log'", required=False, type=str, default='aretes.log')
    parser.add_argument('-n', '--new', help="delete current database and log", required=False, action='store_true')
    parser.add_argument('-c', '--clean', help="delete temporary file directory", required=False, action='store_true')

    args = parser.parse_args()
 
    if args.clean:
        if os.path.isdir("./tmp"):
            shutil.rmtree("./tmp")
    if args.new:
        if os.path.isfile(args.database):
            os.remove(args.database)
        if os.path.isfile(args.log):
            os.remove(args.log)
    else:
        daemon = Daemon(port=args.port, database=args.database, log=args.log)
        daemon.run()
