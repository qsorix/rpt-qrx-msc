#!/usr/bin/env python
# coding=utf-8

from elixir import *

class Test(Entity):
    using_options(tablename='tests')

    name = Field(Unicode(128), required=True)
    duration = Field(Integer, required=True)
    start = Field(DateTime, required=True)

    tasks = OneToMany('Task')
    commands = OneToMany('Command')
    files = OneToMany('File')

    def __repr__(self):
        return '<Test "%s" (%s | %s)>' % (self.name, self.start, self.duration)

class Task(Entity):
    using_options(tablename='tasks')

    command = Field(Unicode(128), required=True)
    name = Field(Unicode(128), required=True)
    file_output = Field(Boolean, default=False)
    file_path = Field(Unicode(128))
    output = Field(LargeBinary)
    start = Field(Integer, required=True)
    pid = Field(Integer)
    
    test = ManyToOne('Test')

    def __repr__(self):
        return '<Task "%s">' % self.command

class Command(Entity):
    using_options(tablename='commands')

    command = Field(Unicode(128), required=True)
    name = Field(Unicode(128), required=True)
    output = Field(LargeBinary)
    
    test = ManyToOne('Test')

    def __repr__(self):
        return '<Command "%s">' % self.command


class File(Entity):
    using_options(tablename='files')

    name = Field(Unicode(128), required=True)
    size = Field(Integer, required=True)
    file_output = Field(Boolean, default=False)
    file_path = Field(Unicode(128))
    content = Field(LargeBinary, deferred=True)

    test = ManyToOne('Test')

    def __repr__(self):
        return '<File "%s" (%d)>' % (self.name, self.size)
