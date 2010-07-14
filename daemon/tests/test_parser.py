#!/usr/bin/env python
# coding=utf-8

import daemon.parser as prs
import py

def test_correct_test():
    parser = prs.Parser()
    type, dict, command = parser.parse('test @{id=test}')
    assert type == 'test'
    assert 'id' in dict
    assert dict['id'] == 'test'
    assert command == None

def test_correct_task():
    parser = prs.Parser()
    type, dict, command = parser.parse('task @{id=task} @{in=5} command -ls *()!#$%^&', parent='test')
    assert type == 'task'
    assert 'id' in dict
    assert dict['id'] == 'task'
    assert 'in' in dict
    assert dict['in'] == 5
    assert command == 'command -ls *()!#$%^&'

def test_correct_start():
    parser = prs.Parser()
    type, dict, command = parser.parse('start @{id=start} @{at=2010-07-14.21:21:32} @{duration=10}')
    assert type == 'start'
    assert 'id' in dict
    assert dict['id'] == 'start'
    assert 'at' in dict
    assert dict['at'] == '2010-07-14.21:21:32'
    assert 'duration' in dict
    assert dict['duration'] == 10

def test_correct_task_results():
    parser = prs.Parser()
    type, dict, command = parser.parse('task @{id=task}', parent='results')
    assert type == 'task'
    assert 'id' in dict
    assert dict['id'] == 'task'

def test_task_with_no_parent():
    parser = prs.Parser()
    py.test.raises(prs.TypeError, parser.parse, 'task @{id=task} @{in=5}')

def test_with_no_id():
    parser = prs.Parser()
    py.test.raises(prs.ParamError, parser.parse, 'test @{sth=else}')

def test_without_required_param():
    parser = prs.Parser()
    py.test.raises(prs.ParamError, parser.parse, 'task @{id=task}', parent='test')

def test_with_too_many_params():
    parser = prs.Parser()
    py.test.raises(prs.ParamError, parser.parse, 'task @{id=task} @{in=5} @{every=5}', parent='test')

def test_unknown_line():
    parser = prs.Parser()
    py.test.raises(prs.LineError, parser.parse, 'unknown line')

def test_unknown_type():
    parser = prs.Parser()
    py.test.raises(prs.TypeError, parser.parse, 'unknown @{id=unknown}')

def test_unknown_param():
    parser = prs.Parser()
    py.test.raises(prs.ParamError, parser.parse, 'test @{id=test} @{unknown=test}')

def test_unwanted_command():
    parser = prs.Parser()
    py.test.raises(prs.CommandError, parser.parse, 'task @{id=test} ls -al', parent='results')

