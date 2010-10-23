#!/usr/bin/env python
# coding=utf-8

from elixir import *

def init(filename):
    metadata.bind = 'sqlite:///' + filename
    setup_all()
    create_all()

def commit():
    session.commit()

class Test(Entity):
    using_options(tablename='tests')

    nodes = OneToMany('Node')

    id = Field(String, primary_key=True)
    start_time = Field(DateTime, required=True)
    duration = Field(Interval, required=True)
    comment = Field(String, required=False, default=None)


class Node(Entity):
    using_options(tablename='nodes')

    test = ManyToOne('Test')
    commands = OneToMany('Command')

    node = Field(String, required=True)
    start_time = Field(DateTime, required=True)
    duration = Field(Interval, required=True)


class Command(Entity):
    using_options(tablename='commands', auto_primarykey='cmd_id')

    node = ManyToOne('Node')
    invocations = OneToMany('Invocation')

    id = Field(String, required=True)
    phase = Field(String, required=True)
    type = Field(String, required=True)
    value = Field(String, required=True)


class Invocation(Entity):
    using_options(tablename='invocations')

    command = ManyToOne('Command')

    output = Field(LargeBinary)
    start_time = Field(DateTime, required=True)
    duration = Field(Interval)
    return_code = Field(Integer)


