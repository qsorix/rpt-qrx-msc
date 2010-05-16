#!/usr/bin/env python
# coding=utf-8

from elixir import *

metadata.bind = "sqlite://database.db"
metadata.bind.echo = True

class Test(Entity):
    using_options(tablename='tests')

    id = Field(Integer, primary_key=True)
    duration = Field(Integer, required=True)
    start = Field(DateTime, required=True)

    tasks = OneToMany('Task')
    files = OneToMany('File')

    def __repr__(self):
        return '<Test %s>' % self.id

class Task(Entity):
    using_options(tablename='tasks')

    command = Field(Unicode(128), required=True)
    output = Field(Binary, deferred=True)
    
    test = ManyToOne('Test')

    def __repr__(self):
        return '<Task "%s">' % self.command

class File(Entity):
    using_options(tablename='files')

    name = Field(Unicode(128), required=True)
    content = Field(Binary, deferred=True)

    test = ManyToOne('Test')

    def __repr__(self):
        return '<File "%s">' % self.name
