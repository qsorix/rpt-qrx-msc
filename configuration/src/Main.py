#!/usr/bin/env python

from config import Configuration
from command import Executer
from controller import Controller
from common import Exceptions

import sys
import getopt
import argparse
import py.path

def load_plugins(paths):
    for path in paths:
        for f in py.path.local(path).visit('*.py'):
            f.pyimport()

if __name__ == "__main__":
    plugins = ['plugins']

    parser = argparse.ArgumentParser(prog='Main.py')
    parser.add_argument('-c', '--config',   help='configuration files', required=True, nargs='+')
    parser.add_argument('--plugins', help='plugins path', required=False, nargs='+', default=[])

    args = parser.parse_args()

    load_plugins(plugins + args.plugins)

    try:
        c = Configuration.Configuration()
        configured_test = c.read(args.config)
        configured_test.sanity_check()

        e = Executer.Executer()
        prepared_commands = e.process( configured_test )
        #TODO: prepared_commands.sanity_check()

        for (host, commands) in prepared_commands.items():
            configured_test.hosts[host].commands = commands
        ctrl = Controller.Controller()
        ctrl.run(configured_test)

    except Exceptions.ConfigurationError as e:
        print 'Configuration error:'
        print e
        if e.traceback:
            print '-'*60
            print e.traceback,
            print '-'*60
        sys.exit(2)

    except Exceptions.MissingPluginError as e:
        print 'Plugin not found:'
        print e


