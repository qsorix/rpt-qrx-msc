from config.Model import destroy_model, create_model, get_model, add_host, Host
from common import Exceptions

import py

def test_add_host():
    destroy_model()
    create_model('test-model')

    add_host('foo')
    assert len(get_model().hosts()) == 1
    assert get_model().hosts()[0].name() == 'foo'

def test_no_duplicates():
    destroy_model()
    create_model('test-model')

    add_host('foo')
    py.test.raises(Exceptions.NameExistsError, add_host, 'foo')

def test_host_interface():
    h = Host('alice', arg='value')
    assert h.name() == 'alice'
    assert h.attributes() == {'arg': 'value'}

    i = h.add_interface('eth0', arg='value')
    assert i.name() == 'eth0'
    assert i.attributes() == {'arg': 'value'}
    assert i == h.interface('eth0')

def test_no_dublicated_interfaces():
    h = Host('alice')
    h.add_interface('eth0')
    py.test.raises(Exceptions.NameExistsError, h.add_interface, 'eth0')

