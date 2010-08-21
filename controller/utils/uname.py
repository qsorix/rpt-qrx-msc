#!/usr/bin/env python
# coding=utf-8

from common.Hooks import HookPlugin

class Uname(HookPlugin):
    hook_name = 'uname'

    def visit_configured_test(self, configured_test):
        for host in configured_test.hosts.values():
            host.commands.add_check('uname -a')
