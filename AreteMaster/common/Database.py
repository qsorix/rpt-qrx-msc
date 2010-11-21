#!/usr/bin/env python
# coding=utf-8

from elixir import *
import datetime

def init(filename):
    metadata.bind = 'sqlite:///' + filename
    setup_all()
    create_all()

def store_test(configured_test):
    Test(id=unicode(configured_test.test_uuid),
         start_time=datetime.datetime.now(),
         comment = configured_test.comment_message,
         model=configured_test.model['name'],
         laboratory=configured_test.laboratory['name'],
         schedule=configured_test.schedule['name'],
         mapping=configured_test.mapping['name'])
    commit();

def commit():
    session.commit()


class Test(Entity):
    using_options(tablename='tests')

    nodes = OneToMany('Node')

    id = Field(String, primary_key=True)
    start_time = Field(DateTime, required=True)
    comment = Field(String, required=False, default=None)

    model = Field(String, required=True)
    laboratory = Field(String, required=True)
    schedule = Field(String, required=True)
    mapping = Field(String, required=True)


class Node(Entity):
    using_options(tablename='nodes')

    test = ManyToOne('Test')
    commands = OneToMany('Command')

    node = Field(String, required=True)
    start_time = Field(DateTime, required=False, default=None)
    duration = Field(Interval, required=False, default=None)


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


