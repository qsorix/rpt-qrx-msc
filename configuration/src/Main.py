import Configuration
import Model
import Mapping
import Schedule

c = Configuration.Configuration()

c.read('test_model', 'test_network', 'test_mapping', 'test_schedule')

print 'Model:'
for l in Model.model.links():
    print '%s.%s --- %s.%s' % (l.first().host().name(), l.first().name(), l.second().host().name(), l.second().name())

print 'Mapping:'
for b in Mapping.mapping.bindings():
    print b.model().name()
    print b.model().attributes()
    print b.model().interfaces()
    print Schedule.schedule.host_schedule(b.model().name())
    print b.network().name()
    print b.network().attributes()
    print b.model().interfaces()
    print "---"
