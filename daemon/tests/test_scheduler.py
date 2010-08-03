#!/usr/bin/env python
# coding=utf-8

import py
import ConfigParser

from daemon.Models import *
from modules.Scheduler import Scheduler
from common.Exceptions import *

def prepare_database():
    metadata.bind = "sqlite:///daemon.db"
    setup_all()
    create_all()

def test_correct_subst_cmd():
    prepare_database()
    scheduler = Scheduler(Test.get_by(id='666'))
    result = scheduler._subst('abc @{setup.command} cba')

    assert result == "abc echo 'setup' cba"
 
def test_subst_bad_id():
    prepare_database()
    scheduler = Scheduler(Test.get_by(id='666'))

    py.test.raises(ResolvError, scheduler._subst, 'abc @{bad.command} cba')

def test_subst_cmd_bad_param_name():
    prepare_database()
    scheduler = Scheduler(Test.get_by(id='666'))

    py.test.raises(ResolvError, scheduler._subst, 'abc @{check1.bad} cba')

def test_correct_subst_file():
    prepare_database()
    scheduler = Scheduler(Test.get_by(id='333'))
    result = scheduler._subst('abc @{file.path} cba')

    config = ConfigParser.SafeConfigParser()
    config.read('daemon.cfg')
    tmpdir = config.get('Daemon', 'tmpdir')

    assert result == "abc " + tmpdir + "/333_file cba"
 
def test_subst_file_bad_param_name():
    prepare_database()
    scheduler = Scheduler(Test.get_by(id='333'))

    py.test.raises(ResolvError, scheduler._subst, 'abc @{file.bad} cba')
