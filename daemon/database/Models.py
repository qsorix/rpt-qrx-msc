#!/usr/bin/env python
# coding=utf-8

from elixir import *

class Test(Entity):
    using_options(tablename='tests')

    id = Field(Unicode(128), required=True, primary_key=True)
    start_time = Field(DateTime, default=None, required=False)
    duration = Field(Integer, default=None, required=False)

    files = OneToMany('File', cascade='delete')
    commands = OneToMany('Command', cascade='delete')

    def __repr__(self):
        return '<Test "%s">' % self.id

class File(Entity):
    using_options(tablename='files')

    id = Field(Unicode(128), required=True, primary_key=True)
    size = Field(Integer, required=True)
    path = Field(Unicode(128), default=None)

    test = ManyToOne('Test', primary_key=True)

    def __repr__(self):
        return '<File "%s" (%d)>' % (self.id, self.size)

class Output(Entity):
    using_options(tablename='outputs')

    content = Field(LargeBinary, default=None)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Output for "%s">' % (self.command.id)
    
class Returncode(Entity):
    using_options(tablename='returncodes')

    content = Field(Integer, default=None)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Returncode for "%s">' % (self.command.id)
    
class StartTime(Entity):
    using_options(tablename='start_times')

    content = Field(DateTime, default=None)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Start time for "%s">' % (self.command.id)
    
class Duration(Entity):
    using_options(tablename='durations')

    content = Field(Integer, default=None)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Duration for "%s">' % (self.command.id)

class Command(Entity):
    using_options(tablename='commands')

    id = Field(Unicode(128), required=True, primary_key=True)
    command = Field(Unicode(128), required=True)

    test = ManyToOne('Test', primary_key=True)
    outputs = OneToMany('Output')
    returncodes = OneToMany('Returncode')
    start_times = OneToMany('StartTime')
    durations = OneToMany('Duration')

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

    run = Field(Unicode(128), required=True)
    pid = Field(Integer, default=None)
    
    def __repr__(self):
        return '<Task "%s": %s>' % (self.id, self.command)

class Clean(Command):
    using_options(inheritance='multi', tablename='clean_commands')

    def __repr__(self):
        return '<Clean "%s": %s>' % (self.id, self.command)
