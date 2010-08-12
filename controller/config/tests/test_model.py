from config.Model import destroy_model, create_model, get_model, add_host, add_link, Host
from common import Exceptions

import py

def test_add_host():
    destroy_model()
    create_model('test-model')

    add_host('foo')
    assert len(get_model().hosts()) == 1
    assert get_model().hosts()[0]['name'] == 'foo'

def test_no_duplicates():
    destroy_model()
    create_model('test-model')

    add_host('foo')
    py.test.raises(Exceptions.NameExistsError, add_host, 'foo')

def test_host_interface():
    h = Host('alice', arg='value')
    assert h['name'] == 'alice'
    assert h['arg'] ==  'value'

    i = h.add_interface('eth0', arg='value')
    assert i['name'] == 'eth0'
    assert i['arg'] ==  'value'
    assert i == h.interface('eth0')

def test_no_dublicated_interfaces():
    h = Host('alice')
    h.add_interface('eth0')
    py.test.raises(Exceptions.NameExistsError, h.add_interface, 'eth0')

def test_link_by_name():
    destroy_model()
    create_model('test-model')

    t1 = add_host('test1')
    t2 = add_host('test2')

    t1.add_interface('eth1')
    t2.add_interface('eth2')

    py.test.raises(Exceptions.ConfigurationError, add_link, 'foo', 'bar')
    py.test.raises(Exceptions.ConfigurationError, add_link, 'test1', 'test2')
    py.test.raises(Exceptions.ConfigurationError, add_link, 'test1.', 'test2.')
    py.test.raises(Exceptions.ConfigurationError, add_link, 'test1.eth2', 'test2.eth1')
    py.test.raises(Exceptions.ConfigurationError, add_link, 'test1.eth1', 'test2.eth1')

    link = add_link('test1.eth1', 'test2.eth2')

    assert link.first()  == t1.interface('eth1')
    assert link.second() == t2.interface('eth2')
