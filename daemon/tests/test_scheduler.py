#!/usr/bin/env python
# coding=utf-8

import nose
from nose.tools import raises
import ConfigParser

from common.Exceptions import *
from daemon.Models import *
from daemon.Daemon import setup_database, setup_config
from modules.Scheduler import Scheduler

class TestSubst:
    @classmethod
    def setUpClass(self):
        setup_database()
        setup_config()
        config = ConfigParser.SafeConfigParser()
        config.read('daemon.cfg')
        self.tmpdir = config.get('Daemon', 'tmpdir')
        self.test = Test(id=u'test_subst')
        Check(id=u'check', command=u'echo check', test=self.test)
        File(id=u'file', size='123', path=unicode(self.tmpdir+'/subst_file'), test=self.test)
        session.commit()
        self.scheduler = Scheduler(self.test)

    def test_correct_subst_cmd(self):
        result = self.scheduler._subst(u'abc @{check.command} cba')
        assert result == 'abc echo check cba'

    @raises(ResolvError)
    def test_subst_bad_id(self):
        self.scheduler._subst(u'abc @{bad.command} cba')

    @raises(ResolvError)
    def test_subst_cmd_bad_param_name(self):
        self.scheduler._subst(u'abc @{check.bad} cba')

    def test_correct_subst_file(self):
        result = self.scheduler._subst(u'abc @{file.path} cba')
        assert result == 'abc ' + self.tmpdir + '/subst_file cba'
     
    @raises(ResolvError)
    def test_subst_file_bad_param_name(self):
        self.scheduler._subst(u'abc @{file.bad} cba')

    @classmethod
    def tearDownClass(self):
        session.delete(self.test)
        session.commit()

class TestOutput:
    @classmethod
    def setUpClass(self):
        setup_database()
        self.test = Test(id=u'test_output')
        self.check1 = Check(id=u'check1', command=u'echo check', test=self.test)
        self.check2 = Check(id=u'check2', command=u'which notexistingone', test=self.test)
        self.task1  = Task (id=u'task1',  command=u'echo task', run=u'in 0', test=self.test)
        self.task2  = Task (id=u'task2',  command=u'which notexistingone', run=u'in 2', test=self.test)
        session.commit()
        self.scheduler = Scheduler(self.test)

    def test_correct_run_cmd(self):
        self.scheduler._run_command(self.check1)
        print repr(self.check1.output)
        assert self.check1.output == 'check'

    @raises(CheckError)
    def test_run_bad_cmd(self):
        self.scheduler._run_command(self.check2)
        assert self.check2.output == 'notexistingone not found\n'

#    def test_run_task():
#        self.scheduler._run_task(self.task1)
#        assert task1.output == 'task\n'

#    @raises(CheckError)
#    def test_run_bad_task():
#        self.scheduler._run_command(self.task2)
#        assert self.task2.output == 'notexistingone not found\n'

    @classmethod
    def tearDownClass(self):
        session.delete(self.test)
        session.commit()
