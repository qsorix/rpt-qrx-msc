#!/usr/bin/env python
# coding=utf-8

from config import Configuration
from config import Global
from command import Generator
from controller import Controller
from common import Exceptions
from common.Hooks import HookPlugin
from common import Database

import sys
import os
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
    plugins = [sys.path[0]+os.sep+'plugins']

    parser = argparse.ArgumentParser(prog='arete')
    parser.add_argument('-c', '--config',   help='configuration files', required=True, nargs='+')
    parser.add_argument('-s', '--set', help='set a test parameter, the format is name=value', required=False, nargs='+', default=[])
    parser.add_argument('--askparams', help='ask for values of missing parameters', required=False, action='store_true', default=False, dest='ask_parameters')
    parser.add_argument('--plugins', help='plugins path', required=False, nargs='+', default=[])
    parser.add_argument('--hooks', help='names of the hooks to run', required=False, nargs='+', default=[])
    parser.add_argument('--map', help='allows you to specify mapping on command line in the format model:device', required=False, nargs='+', default=[])
    parser.add_argument('-m', '--message', help='specify comment message for this execution of test', required=False, default=None)
    parser.add_argument('-d', '--database', help='path to results database (sqlite file)', required=False, default="arete.db")

    args = parser.parse_args()

    load_plugins(plugins + args.plugins)

    try:
        Global.parameters.prompt_parameters(args.ask_parameters)
        consume_parameters(args.set)

        # read configuration
        configured_test = Configuration.Configuration().read(args.config, args.map)
        configured_test.comment_message = args.message

        # generate commands
        Generator.Generator().process( configured_test )

        # run hooks
        for hook_name in args.hooks:
            HookPlugin.lookup(hook_name)().visit_configured_test(configured_test)

        # initialize database
        Database.init(args.database)
        Database.store_test(configured_test)

        # perform test
        Controller.Controller().run(configured_test)

    except Exceptions.MissingPluginError as e:
        print 'Plugin not found:'
        print e

    except Exceptions.ConfigurationError as e:
        print 'Configuration error:'
        print e
        if e.traceback:
            print '-'*60
            print e.traceback,
            print '-'*60
        sys.exit(2)

    except Exceptions.SlaveError as e:
        print 'Slave communication error:'
        print e
        if e.traceback:
            print '-'*60
            print e.traceback,
            print '-'*60
        sys.exit(3)

    except Exception as e:
        print 'Error: ', e
        raise
