import config.Model as Model
import config.Laboratory as Laboratory

from config.Mapping import create_mapping, destroy_mapping, get_mapping, bind

import py

def clear():
    Model.destroy_model()
    Laboratory.destroy_laboratory()

    Model.create_model('test-model')
    Laboratory.create_laboratory('test-lab')

    destroy_mapping()
    create_mapping('test-map-model-to-lab')

def test_binding():
    clear()

    m = Model.add_host('alice')
    n = Laboratory.add_device('node1')
    bind(m, n)

    assert(m.bound() == n)
    assert(n.bound() == m)
    assert len(get_mapping().bindings()) == 1

def test_no_dublicated_mapping():
    clear()

    m = Model.add_host('alice')
    n = Laboratory.add_device('node1')
    bind(m, n)
    bind(m, n)
    bind(n, m)
    assert len(get_mapping().bindings()) == 1
