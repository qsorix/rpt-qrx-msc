#!/usr/bin/env python
# coding=utf-8

import sys
import re
import os
import ConfigParser
from models import *

def subst(test, substr):
    value = substr

    rsubst = re.compile('^(?P<pre>.+)?\@\{(?P<subst>.+)\}(?P<post>.+)?$')

    while rsubst.match(value):
        m = rsubst.match(value)
        pre = m.group('pre')
        post = m.group('post')
        str = m.group('subst')

        value = ''
        if pre: value += pre

        m = re.match('^((?P<name>[a-zA-Z0-9_]+)\.)?(?P<param>[a-zA-Z0-9_]+)$', unicode(str))

        name = m.group('name')
        param = unicode(m.group('param'))

        if name:
            file = File.query.filter_by(name=name, test=test).first()
            task = Task.query.filter_by(name=name, test=test).first()
            cmd  = Command.query.filter_by(name=name, test=test).first()

            if file and param in ['name', 'size']:
                exec('tmp = file.%s' % param)

            elif task and param in ['name', 'command', 'start', 'pid']:
                exec('tmp = task.%s' % param)

            elif cmd and param in ['name', 'command']:
                exec('tmp = cmd.%s' % param)

        else:
            if os.path.isfile('daemon.cfg') and param in ['tmpdir']:
                config = ConfigParser.SafeConfigParser()
                config.read('daemon.cfg')

                exec('tmp = config.get(\'Daemon\', \'%s\')' % param)

        value += unicode(tmp)
        if post: value += post

    return value

def join_args(args):
    join = False
    symbols = ['"', '\'', '`']
    delete = []

    for i in range(len(args)):
        if join:
            args[first] += ' ' + args[i]
            if args[i].endswith(symbol):
                join = False
            delete.append(args[i])
        elif args[i][0] in symbols:
            first = i
            symbol = args[i][0]
            join = True

    for arg in delete:
        args.remove(arg)

def name_exists(test, name):
    if Task.query.filter_by(name=unicode(name), test=test).all() +\
        Command.query.filter_by(name=unicode(name), test=test).all() +\
        File.query.filter_by(name=unicode(name), test=test).all():
        return True
    return False

