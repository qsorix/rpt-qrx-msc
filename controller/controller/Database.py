#!/usr/bin/env python
# coding=utf-8

from elixir import *

class Test(Entity):
    using_options(tablename='tests')

    id = Field(Unicode(128), primary_key=True)
    comment = Field(Unicode(128), required=False, default=None)
    start_time = Field(DateTime, required=True)
    duration = Field(Integer, required=True)

    commands = OneToMany('Command')

    def __repr__(self):
        return '<Test "%s">' % self.id

class Output(Entity):
    using_options(tablename='outputs')

    content = Field(LargeBinary, required=True)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Output for "%s">' % (self.command.id)
    
class Returncode(Entity):
    using_options(tablename='returncodes')

    content = Field(Integer, required=True)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Returncode for "%s">' % (self.command.id)
    
class StartTime(Entity):
    using_options(tablename='start_times')

    content = Field(DateTime, required=True)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Start time for "%s">' % (self.command.id)
    
class Duration(Entity):
    using_options(tablename='durations')

    content = Field(Integer, required=True)
    
    command = ManyToOne('Command')
    
    def __repr__(self):
        return '<Duration for "%s">' % (self.command.id)

class Command(Entity):
    using_options(tablename='commands')

    id = Field(Unicode(128), primary_key=True)
#    command = Field(Unicode(128), required=True)
    type = Field(Unicode(128), required=True)

    test = ManyToOne('Test', primary_key=True)
    outputs = OneToMany('Output')
    returncodes = OneToMany('Returncode')
    start_times = OneToMany('StartTime')
    durations = OneToMany('Duration')

    def __repr__(self):
        return '<Command "%s">' % (self.id)
