#!/usr/bin/env python
# coding=utf-8

import nose
from nose.tools import raises

from modules.Parser import Parser
from common.Exceptions import *

class TestParser:
    @classmethod
    def setUpClass(self):
        self.parser = Parser()

    def test_correct_test(self):
        type, dict = self.parser.parse('test @{id=test}')
        assert type == 'test'
        assert 'id' in dict
        assert dict['id'] == 'test'

    def test_correct_task(self):
        type, dict = self.parser.parse('task @{id=task} @{run=in 5} ls -al *()!#$%^&', parent='test')
        assert type == 'test_task'
        assert 'id' in dict
        assert dict['id'] == 'task'
        assert 'run' in dict
        assert dict['run'] == 'in 5'
        assert dict['command'] == 'ls -al *()!#$%^&'

    def test_correct_start(self):
        type, dict = self.parser.parse('start @{id=start} @{run=at 2010-07-14 21:21:32} @{end=duration 10}')
        assert type == 'start'
        assert 'id' in dict
        assert dict['id'] == 'start'
        assert 'run' in dict
        assert dict['run'] == 'at 2010-07-14 21:21:32'
        assert 'end' in dict
        assert dict['end'] == 'duration 10'

    def test_correct_task_results(self):
        type, dict = self.parser.parse('get @{id=task}', parent='results')
        assert type == 'results_get'
        assert 'id' in dict
        assert dict['id'] == 'task'

    def test_correct_test_end(self):
        type, dict = self.parser.parse('end', parent='test')
        assert type == 'test_end'
        assert dict == {}

    def test_correct_results_end(self):
        type, dict = self.parser.parse('end', parent='results')
        assert type == 'results_end'
        assert dict == {}

    @raises(TypeError)
    def test_task_with_no_parent(self):
        self.parser.parse('task @{id=task} @{run=in 5}')

    @raises(ParamError)
    def test_with_no_id(self):
        self.parser.parse('test @{sth=else}')

    @raises(ParamError)
    def test_without_required_param(self):
        self.parser.parse('task @{id=task}', parent='test')

    @raises(ParamError)
    def test_with_too_many_params(self):
        self.parser.parse('task @{id=task} @{run=at 5} @{run=every 5}', parent='test')

    @raises(TypeError)
    def test_unknown_line(self):
        self.parser.parse('unknown line')

    @raises(TypeError)
    def test_unknown_type(self):
        self.parser.parse('unknown @{id=unknown}')

    @raises(ParamError)
    def test_unknown_param(self):
        self.parser.parse('test @{id=test} @{unknown=test}')

