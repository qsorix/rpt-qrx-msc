#!/usr/bin/env python
# coding=utf-8

from elixir import *

class Test(Entity):
    using_options(tablename='tests')

    id = Field(Unicode(128), required=True)
    started_at = Field(DateTime)
    length = Field(Integer)

    files = OneToMany('File')
    commands = OneToMany('Command')

    def __repr__(self):
        return '<Test "%s">' % self.name

class File(Entity):
    using_options(tablename='files')

    id = Field(Unicode(128), required=True)
    size = Field(Integer, required=True)
#    file_path = Field(Unicode(128), default=None)
    content = Field(LargeBinary, deferred=True)

    test = ManyToOne('Test')

    def __repr__(self):
        return '<File "%s" (%d)>' % (self.name, self.size)

class Command(Entity):
    using_options(tablename='commands')

    id = Field(Unicode(128), required=True)
    command = Field(Unicode(128), required=True)
    
    test = ManyToOne('Test')

    def __repr__(self):
        return '<Command "%s": %s >' % (self.id, self.command)

class Check(Command):
    using_options(inheritance='multi', tablename='check_commands')

    result = Field(Boolean, default=True)

    def __repr__(self):
        return '<Check "%s": %s>' % (self.id, self.command)

class Setup(Command):
    using_options(inheritance='multi', tablename='setup_commands')

    result = Field(Boolean, default=True)

    def __repr__(self):
        return '<Setup "%s": %s>' % (self.id, self.command)

class Task(Command):
    using_options(inheritance='multi', tablename='tasks')

#    file_path = Field(Unicode(128), default=None)
    output = Field(LargeBinary)
    trigger_type = Field(Integer, required=True) # 0 - in, 1 - every
    trigger_value = Field(Integer, default=0)
    pid = Field(Integer)
    
    test = ManyToOne('Test')

    def __repr__(self):
        return '<Task "%s": %s>' % (self.id, self.command)

class Clean(Command):
    using_options(inheritance='multi', tablename='clean_commands')

    result = Field(Boolean, default=True)

    def __repr__(self):
        return '<Clean "%s": %s>' % (self.id, self.command)

