#@name("Peers")
def model(m):
    alice = m.host("alice")
    bob   = m.host("bob")

    m.link(alice, bob)

#@name("Lan2")
def model(m):
    east = m.host("east", count=4)
    west = m.host("west", count=4)

    router = m.host("router")

    router.interface(
            name  = 'p0',
            delay = '10ms',
            loss  = 0.1)

    router.interface(
            name  = 'p1',
            delay = '5ms',
            loss  = 0.2)

    m.link_all(router.p0, east)
    m.link_all(router.p1, west)

def network(n):
    n.host(
            name  = 'defteros',
            ip    = '192.168.6.1',
            ports = 'eth0')

    n.host(
            name  = 'marvin',
            ip    = '192.168.6.2',
            ports = 'eth0 wlan0')

    n.host_range(
            name = 'swarm',
            ip_begin = '192.168.1.1',
            ip_end   = '192.168.1.32')

#@for("Peers")
def mapping(m):
    m.map('alice', 'defteros')
    m.map('bob', 'marvin')

#@for("Lan2")
def mapping(m):
    m.map_many('east', 'swarm')
    m.map_many('west', 'swarm')
    m.map('router', 'marvin').interface('p0', 'eth0').interface('p1', 'wlan0')

