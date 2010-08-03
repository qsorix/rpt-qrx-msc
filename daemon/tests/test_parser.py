#!/usr/bin/env python
# coding=utf-8

from modules.Parser import Parser
from common.Exceptions import *
import py

def test_correct_test():
    parser = Parser()
    type, dict = parser.parse('test @{id=test}')
    assert type == 'test'
    assert 'id' in dict
    assert dict['id'] == 'test'

def test_correct_task():
    parser = Parser()
    type, dict = parser.parse('task @{id=task} @{run=in 5} ls -al *()!#$%^&', parent='test')
    assert type == 'test_task'
    assert 'id' in dict
    assert dict['id'] == 'task'
    assert 'run' in dict
    assert dict['run'] == 'in 5'
    assert dict['command'] == 'ls -al *()!#$%^&'

def test_correct_start():
    parser = Parser()
    type, dict = parser.parse('start @{id=start} @{run=at 2010-07-14 21:21:32} @{end=duration 10}')
    assert type == 'start'
    assert 'id' in dict
    assert dict['id'] == 'start'
    assert 'run' in dict
    assert dict['run'] == 'at 2010-07-14 21:21:32'
    assert 'end' in dict
    assert dict['end'] == 'duration 10'

def test_correct_task_results():
    parser = Parser()
    type, dict = parser.parse('get @{id=task}', parent='results')
    assert type == 'results_get'
    assert 'id' in dict
    assert dict['id'] == 'task'

def test_correct_test_end():
    parser = Parser()
    type, dict = parser.parse('end', parent='test')
    assert type == 'test_end'
    assert dict == {}

def test_correct_results_end():
    parser = Parser()
    type, dict = parser.parse('end', parent='results')
    assert type == 'results_end'
    assert dict == {}

def test_task_with_no_parent():
    parser = Parser()
    py.test.raises(TypeError, parser.parse, 'task @{id=task} @{run=in 5}')

def test_with_no_id():
    parser = Parser()
    py.test.raises(ParamError, parser.parse, 'test @{sth=else}')

def test_without_required_param():
    parser = Parser()
    py.test.raises(ParamError, parser.parse, 'task @{id=task}', parent='test')

def test_with_too_many_params():
    parser = Parser()
    py.test.raises(ParamError, parser.parse, 'task @{id=task} @{run=at 5} @{run=every 5}', parent='test')

def test_unknown_line():
    parser = Parser()
    py.test.raises(TypeError, parser.parse, 'unknown line')

def test_unknown_type():
    parser = Parser()
    py.test.raises(TypeError, parser.parse, 'unknown @{id=unknown}')

def test_unknown_param():
    parser = Parser()
    py.test.raises(ParamError, parser.parse, 'test @{id=test} @{unknown=test}')

