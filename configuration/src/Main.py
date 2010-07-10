#!/usr/bin/env python



from config import Configuration
from command import Executer
from controller import Controller
from common import Exceptions

import sys
import getopt
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Main.py')
    parser.add_argument('-m', '--model',    help='model file',    required=True)
    parser.add_argument('-n', '--network',  help='network file',  required=True)
    parser.add_argument('-p', '--mapping',  help='mapping file',  required=True)
    parser.add_argument('-s', '--schedule', help='schedule file', required=True)

    args = parser.parse_args()

    try:
        c = Configuration.Configuration()
        configured_test = c.read(args.model, args.network, args.mapping, args.schedule)
        configured_test.sanity_check()

    except Exceptions.ConfigurationError as e:
        print 'Configuration error:'
        print e
        print '-'*60
        print e.traceback,
        print '-'*60
        sys.exit(2)

    e = Executer.Executer()
    prepared_commands = e.process( configured_test )
    #TODO: prepared_commands.sanity_check()

    for (host, commands) in prepared_commands.items():
        configured_test.hosts[host].commands = commands

    ctrl = Controller.Controller()
    ctrl.run(configured_test)

