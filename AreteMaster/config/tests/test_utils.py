#!/usr/bin/env python
# coding=utf-8

from config.Model import destroy_model, create_model, add_host
from config.Laboratory import destroy_laboratory, create_laboratory, add_device
from config.Utils import resolve_host_name, resolve_device_name, resolve_interface_name, resolve_name

from common import Exceptions

import py

def test_any_name_resolving():
    destroy_model()
    create_model('test-model')

    destroy_laboratory()
    create_laboratory('test-lab')

    h = add_host('test1')
    d = add_device('node1')

    he = h.add_interface('eth')
    de = d.add_interface('eth1')

    assert h == resolve_name('test1')
    assert d == resolve_name('node1')
    assert he == resolve_name('test1.eth', model=True)
    assert he == resolve_name('test1.eth')
    assert de == resolve_name('node1.eth1', laboratory=True)
    assert de == resolve_name('node1.eth1')

    py.test.raises(Exceptions.ConfigurationError, resolve_name, 'foo')
    py.test.raises(Exceptions.ConfigurationError, resolve_name, 'test1.')
    py.test.raises(Exceptions.ConfigurationError, resolve_name, '.test1')

    py.test.raises(Exceptions.ConfigurationError, resolve_name, 'node1.eth1', model=True)
    py.test.raises(Exceptions.ConfigurationError, resolve_name, 'test1.eth', laboratory=True)

def test_name_resolving():
    destroy_model()
    create_model('test-model')

    destroy_laboratory()
    create_laboratory('test-lab')

    h = add_host('test1')
    d = add_device('node1')

    he = h.add_interface('eth')
    de = d.add_interface('eth1')

    assert h == resolve_host_name('test1')
    assert d == resolve_device_name('node1')
    assert he == resolve_interface_name('test1.eth', model=True)
    assert he == resolve_interface_name('test1.eth')
    assert de == resolve_interface_name('node1.eth1', laboratory=True)
    assert de == resolve_interface_name('node1.eth1')

    py.test.raises(Exceptions.ConfigurationError, resolve_host_name, 'foo')
    py.test.raises(Exceptions.ConfigurationError, resolve_host_name, 'node1')
    py.test.raises(Exceptions.ConfigurationError, resolve_host_name, 'test1.')
    py.test.raises(Exceptions.ConfigurationError, resolve_host_name, 'test1 ')
    py.test.raises(Exceptions.ConfigurationError, resolve_host_name, '.test1')

    py.test.raises(Exceptions.ConfigurationError, resolve_device_name, 'foo')
    py.test.raises(Exceptions.ConfigurationError, resolve_device_name, 'test1')
    py.test.raises(Exceptions.ConfigurationError, resolve_device_name, 'node1.')
    py.test.raises(Exceptions.ConfigurationError, resolve_device_name, 'node1 ')
    py.test.raises(Exceptions.ConfigurationError, resolve_device_name, '.node1')

    py.test.raises(Exceptions.ConfigurationError, resolve_interface_name, 'node1.eth1', model=True)
    py.test.raises(Exceptions.ConfigurationError, resolve_interface_name, 'test1.eth', laboratory=True)
