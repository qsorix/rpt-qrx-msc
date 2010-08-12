#!/usr/bin/env python

from config import Configuration
from config import Global
from command import Generator
from controller import Controller
from common import Exceptions
from common.Hooks import HookPlugin

import sys
import getopt
import argparse
import py.path

def load_plugins(paths):
    for path in paths:
        for f in py.path.local(path).visit('*.py'):
            if f.purebasename != '__init__':
                f.pyimport()

def consume_parameters(params):
    for p in params:
        try:
            name, value = p.split('=')
            Global.parameters[name] = value
        except ValueError:
            raise Exceptions.ConfigurationError("Could not understand --set argument '%s'. Use name=value format" % p)

if __name__ == "__main__":
    plugins = ['plugins']

    parser = argparse.ArgumentParser(prog='Main.py')
    parser.add_argument('-c', '--config',   help='configuration files', required=True, nargs='+')
    parser.add_argument('-s', '--set', help='set a test parameter, the format is name=value', required=False, nargs='+', default=[])
    parser.add_argument('--plugins', help='plugins path', required=False, nargs='+', default=[])
    parser.add_argument('--hooks', help='names of the hooks to run', required=False, nargs='+', default=[])

    args = parser.parse_args()

    load_plugins(plugins + args.plugins)

    try:
        consume_parameters(args.set)

        c = Configuration.Configuration()
        configured_test = c.read(args.config)

        e = Generator.Generator()
        prepared_commands = e.process( configured_test )
        #TODO: prepared_commands.sanity_check()

        for (host, commands) in prepared_commands.items():
            configured_test.hosts[host].commands = commands

        for hook_name in args.hooks:
            HookPlugin.lookup(hook_name)().visit_configured_test(configured_test)

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

