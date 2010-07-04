import config.Model as Model
import config.Network as Network

from config.Mapping import mapping, bind

import py

def clear():
    Model.model.clear()
    Network.network.clear()
    mapping.clear()

def test_binding():
    clear()

    m = Model.add_host('alice')
    n = Network.add_host('node1')
    bind(m, n)

    assert(m.bound() == n)
    assert(n.bound() == m)
    assert len(mapping.bindings()) == 1

def test_no_dublicated_mapping():
    clear()

    m = Model.add_host('alice')
    n = Network.add_host('node1')
    bind(m, n)
    bind(m, n)
    bind(n, m)
    assert len(mapping.bindings()) == 1
