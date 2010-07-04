from config.Model import model, add_host, Host
import config.Exceptions as Exceptions

import py

def clear_model():
    model.clear()

def test_add_host():
    clear_model()
    add_host('foo')
    assert len(model.hosts()) == 1
    assert model.hosts()[0].name() == 'foo'

def test_no_duplicates():
    clear_model()
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

