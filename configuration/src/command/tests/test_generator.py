from command.Generator import Generator, HostCommands
from config.Configuration import ConfiguredHost, ConfiguredTest
from config.Model import Host
from config.Laboratory import Device

def test_command_substitutions():
    alice = Host('alice', ip='192.168.6.1')
    alice.add_interface('i0', loss='0.1')

    node1 = Device('node1', hostname='device1')
    node1.add_interface('eth0', type='ethernet', loss='66')

    alice.bind(node1)
    node1.bind(alice)
    alice.interface('i0').bind(node1.interface('eth0'))
    node1.interface('eth0').bind(alice.interface('i0'))

    host = ConfiguredHost()
    host.model = alice
    host.device = node1

    ct = ConfiguredTest()
    ct.hosts = {'alice': host}

    g = Generator()

    def substitute(input, expect):
        assert expect == g._substitute_for_host('alice', input, ct)

    yield substitute, 'foo @{alice.ip}',        'foo 192.168.6.1'
    yield substitute, 'foo @{alice.bogus}',     'foo @{alice.bogus}'
    yield substitute, 'foo @{alice}',           'foo @{alice}'
    yield substitute, 'foo @{alice.hostname}',  'foo device1'
    yield substitute, 'foo @{node1}',           'foo @{node1}'
    yield substitute, 'foo @{node1.hostname}',  'foo @{node1.hostname}'
    yield substitute, 'foo @{alice.eth0}',      'foo @{alice.eth0}'
    yield substitute, 'foo @{alice.eth0.type}', 'foo @{alice.eth0.type}'
    yield substitute, 'foo @{alice.i0.type}',   'foo ethernet'
    yield substitute, 'foo @{alice.i0.loss}',   'foo 0.1'

    # the name attribute is treated differently, we don't want model names in
    # commands, so it should use bound object's name instead
    yield substitute, 'foo @{alice.name}',    'foo node1'
    yield substitute, 'foo @{alice.i0.name}', 'foo eth0'

    yield substitute, 'foo @{alice.i0.loss} @{alice.ip}',   'foo 0.1 192.168.6.1'

    yield substitute, 'foo @{}', 'foo @{}'
    yield substitute, 'foo @{#$#}', 'foo @{#$#}'
    yield substitute, 'foo @{alice.}', 'foo @{alice.}'
    yield substitute, 'foo @{...}', 'foo @{...}'
    yield substitute, 'foo @{alice.i0.loss.}', 'foo @{alice.i0.loss.}'
