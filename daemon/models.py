#!/usr/bin/env python
# coding=utf-8

from elixir import *

metadata.bind = "sqlite:///database.db"
#metadata.bind.echo = True
session.configure(autoflush=False)

class Test(Entity):
    using_options(tablename='tests')

    id = Field(Integer, primary_key=True)
    duration = Field(Integer)
    start = Field(DateTime)

    tasks = OneToMany('Task')
    files = OneToMany('File')

    def __repr__(self):
        return '<Test %s (%s | %s)>' % (self.id, self.start, self.duration)

class Task(Entity):
    using_options(tablename='tasks')

    command = Field(Unicode(128), required=True)
    output = Field(LargeBinary)
    
    test = ManyToOne('Test')

    def __repr__(self):
        return '<Task "%s">' % self.command

class File(Entity):
    using_options(tablename='files')

    name = Field(Unicode(128), required=True)
    length = Field(Integer)
    content = Field(LargeBinary, deferred=True)

    test = ManyToOne('Test')

    def __repr__(self):
        return '<File "%s" (%d)>' % (self.name, self.length)
