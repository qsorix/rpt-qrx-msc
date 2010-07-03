from config import Configuration
from command import Executer

def dump_configuration(c):
    for h in c.hosts():
        print '-- HOST ', h.model.name(), ' --'
        m = h.model
        print '    model {'
        print '        ', m.attributes()
        print '        ', [(i.name(), i.attributes()) for i in m.interfaces().values()]
        print '    }'

        n = h.network
        if n is not None:
            print '    network {'
            print '        ', n.attributes()
            print '        ', [(i.name(), i.attributes()) for i in n.interfaces().values()]
            print '    }'

        s = h.schedule
        if s is not None:
            print '    schedule {'
            print '        ', s
            print '    }'

        print

c = Configuration.Configuration()

c.read('test_model', 'test_network', 'test_mapping', 'test_schedule')

e = Executer.Executer()

for h in c.hosts():
    print h.model.name()
    c = e.generate(h)
    c.dump()

