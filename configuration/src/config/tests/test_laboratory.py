from config.Laboratory import create_laboratory, destroy_laboratory, get_laboratory, add_device, Device
from common import Exceptions

import py

def clear():
    destroy_laboratory()
    create_laboratory('test-lab')

def test_add_device():
    clear()
    add_device('foo')
    assert len(get_laboratory().devices()) == 1
    assert get_laboratory().devices()[0].name() == 'foo'

def test_no_duplicates():
    clear()

    add_device('foo')
    py.test.raises(Exceptions.NameExistsError, add_device, 'foo')

def test_device_interface():
    h = Device('alice', arg='value')
    assert h.name() == 'alice'
    assert h['arg'] == 'value'

    i = h.add_interface('eth0', arg='value')
    assert i.name() == 'eth0'
    assert i['arg'] == 'value'
    assert i == h.interface('eth0')
