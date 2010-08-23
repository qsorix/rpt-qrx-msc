#!/usr/bin/env python
# coding=utf-8

import sys
import argparse

from modules.Daemon import Daemon

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Main.py')
    
    parser.add_argument('-p', '--port', help="use port other than 4567", required=False, nargs='?', type=int, default=4567)
    parser.add_argument('-d', '--database', help="use database file other than 'aretes.db'", required=False, nargs='?', type=str, default='aretes.db')
    parser.add_argument('-l', '--log', help="use log file other than 'aretes.log'", required=False, nargs='?', type=str, default='aretes.log')

    args = parser.parse_args()
    
    daemon = Daemon(port=args.port, database=args.database, log=args.log)
    daemon.run()
