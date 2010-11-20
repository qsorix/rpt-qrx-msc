#!/usr/bin/env python
# coding=utf-8

from elixir import *

class Test(Entity):
    using_options(tablename='tests')

    id = Field(Unicode, required=True, primary_key=True)
    start_time = Field(DateTime, default=None, required=False)
    duration = Field(Integer, default=None, required=False)

    files = OneToMany('File', cascade='delete')
    commands = OneToMany('Command', cascade='delete')

    def __repr__(self):
        return '<Test "%s">' % self.id

class File(Entity):
    using_options(tablename='files')

    id = Field(Unicode, required=True, primary_key=True)
    size = Field(Integer, required=True)
    name = Field(Unicode, required=True)

    test = ManyToOne('Test', primary_key=True)

    def __repr__(self):
        return '<File "%s" (%d)>' % (self.id, self.size)

class Invocation(Entity):
    using_options(tablename='invocations')

    command = ManyToOne('Command')

    output = Field(LargeBinary, default=None)
    start_time = Field(DateTime, required=True)
    duration = Field(Interval, default=None)
    return_code = Field(Integer, default=None)
    
    def __repr__(self):
        return '<Invocation for "%s">' % (self.command.id)

class Command(Entity):
    using_options(tablename='commands')

    id = Field(Unicode, required=True, primary_key=True)
    command = Field(Unicode, required=True)

    test = ManyToOne('Test', primary_key=True)
    invocations = OneToMany('Invocation')

    def __repr__(self):
        return '<Command "%s": %s >' % (self.id, self.command)

class Check(Command):
    using_options(inheritance='multi', tablename='check_commands')

    def __repr__(self):
        return '<Check "%s": %s>' % (self.id, self.command)

class Setup(Command):
    using_options(inheritance='multi', tablename='setup_commands')

    def __repr__(self):
        return '<Setup "%s": %s>' % (self.id, self.command)

class Task(Command):
    using_options(inheritance='multi', tablename='tasks')

    run = Field(Unicode, required=True)
    cmd_type = Field(Unicode, required=True)
    pid = Field(Integer, default=None)
    
    def __repr__(self):
        return '<Task "%s": %s>' % (self.id, self.command)

class Clean(Command):
    using_options(inheritance='multi', tablename='clean_commands')

    def __repr__(self):
        return '<Clean "%s": %s>' % (self.id, self.command)
