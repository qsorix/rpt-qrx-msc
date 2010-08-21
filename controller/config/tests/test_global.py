#!/usr/bin/env python
# coding=utf-8

import config.Global as Global
import StringIO
import sys

def test_parameters_dict():
    Global.parameters['foo'] = 'bar'
    assert Global.parameters['foo'] == 'bar'

def test_parameters_get_secure():
    Global.parameters['pass'] = 'abc'
    assert Global.parameters.get_secure('pass') == 'abc'

def test_parameters_prompt():
    sys.stdin = StringIO.StringIO('alice')

    Global.parameters.prompt_parameters(True)
    assert Global.parameters['missing'] == 'alice'
