#!/usr/bin/env python
# coding=utf-8

from nose.tools import raises

from modules.Parser import parse
from common.Exceptions import *

class TestParser:
    @classmethod
    def setUpClass(self):
        pass

    def test_correct_test(self):
        type, dict = parse('test @{id=test}')
        assert type == 'test'
        assert 'id' in dict
        assert dict['id'] == 'test'

    def test_correct_task(self):
        type, dict = parse('task @{id=task} @{run=at 5} ls -al *()!#$%^&', parent='test')
        assert type == 'test_task'
        assert 'id' in dict
        assert dict['id'] == 'task'
        assert 'run' in dict
        assert dict['run'] == 'at 5'
        assert 'command' in dict
        assert dict['command'] == 'ls -al *()!#$%^&'

    def test_correct_start(self):
        type, dict = parse('start @{id=start} @{run=at 2010-07-14T21:21:32.732193} @{end=duration 10}')
        assert type == 'start'
        assert 'id' in dict
        assert dict['id'] == 'start'
        assert 'run' in dict
        assert dict['run'] == 'at 2010-07-14T21:21:32.732193'
        assert 'end' in dict
        assert dict['end'] == 'duration 10'

    def test_correct_task_results(self):
        type, dict = parse('get @{task.output}', parent='results')
        assert type == 'results_get'
        assert 'command' in dict
        assert dict['command'] == '@{task.output}'

    def test_correct_test_end(self):
        type, dict = parse('end', parent='test')
        assert type == 'test_end'
        assert dict == {}

    def test_correct_results_end(self):
        type, dict = parse('end', parent='results')
        assert type == 'results_end'
        assert dict == {}

    @raises(TypeError)
    def test_task_with_no_parent(self):
        parse('task @{id=task} @{run=in 5}')

    @raises(ParamError)
    def test_with_no_id(self):
        parse('test @{sth=else}')

    @raises(ParamError)
    def test_without_required_param(self):
        parse('task @{id=task}', parent='test')

    @raises(ParamError)
    def test_with_too_many_params(self):
        parse('task @{id=task} @{run=at 5} @{run=every 5}', parent='test')

    @raises(TypeError)
    def test_unknown_line(self):
        parse('unknown line')

    @raises(TypeError)
    def test_unknown_type(self):
        parse('unknown @{id=unknown}')

    @raises(ParamError)
    def test_unknown_param(self):
        parse('test @{id=test} @{unknown=test}')

