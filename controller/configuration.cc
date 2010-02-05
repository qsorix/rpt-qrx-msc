#include "configuration.h"

#include <Poco/Net/DialogSocket.h>
#include <Poco/DOM/NodeList.h>
#include <Poco/DOM/Element.h>
#include <Poco/AutoPtr.h>
#include <boost/lexical_cast.hpp>
#include <iostream>
#include <cassert>
#include <stdexcept>

using Poco::XML::Element;

Configuration::Configuration(Poco::XML::Document const & doc)
{
	Element* root = doc.documentElement();
	if (root->nodeName() != "configuration")
		throw XMLSchemaError("Root element must be named 'configuration'");

	if (Element* hosts = root->getChildElement("hosts"))
        handle_hosts(hosts);
    else
		throw XMLSchemaError("No hosts defined");

	if (Element* test = root->getChildElement("test"))
        handle_test(test);
    else
		throw XMLSchemaError("No test defined");

}

void Configuration::handle_hosts(Element* hosts)
{
	Poco::AutoPtr<Poco::XML::NodeList> pList = hosts->getElementsByTagName("host");
	for(int i=0; i<pList->length(); ++i) {
		handle_host(dynamic_cast<Element*>(pList->item(i)));
	}
}


void Configuration::handle_host(Element* host)
{
	std::string id = host->getAttribute("id");
	if (id.empty())
		throw XMLSchemaError("Host is missing mandatory id argument");

	if(hosts_.count(id))
		throw XMLSchemaError("Host " + id + " appears more than once");

	Host h;
	if (Element *e = host->getChildElement("ip"))
		h.ip = e->innerText();

	if (Element *e = host->getChildElement("name"))
		h.name = e->innerText();

	if (Element *e = host->getChildElement("port"))
		h.port = boost::lexical_cast<int>(e->innerText());

	hosts_.insert(std::make_pair(id,  h));
}

void Configuration::handle_test(Element* test)
{
	if (Element *e = test->getChildElement("duration"))
		test_.duration = boost::lexical_cast<int>(e->innerText());
    else
        throw XMLSchemaError("Test is missing mandatory duration argument");

	Poco::AutoPtr<Poco::XML::NodeList> pListSchedule = test->childNodes();
	for(int i=0; i<pListSchedule->length(); ++i) {
        if(Element *e = dynamic_cast<Element*>(pListSchedule->item(i)))
            if(e->nodeName() == "schedule")
                handle_schedule(e);
	}

	Poco::AutoPtr<Poco::XML::NodeList> pListSetup = test->getElementsByTagName("setup");
	for(int i=0; i<pListSetup->length(); ++i) {
		handle_setup(dynamic_cast<Element*>(pListSetup->item(i)));
	}
}

void Configuration::handle_schedule(Element* sch)
{
	std::string id = sch->getAttribute("id");
	if (id.empty())
		throw XMLSchemaError("Schedule is missing mandatory id argument");

	if(schedules_.count(id))
		throw XMLSchemaError("Schedule " + id + " appears more than once");

    Schedule s;
	Poco::AutoPtr<Poco::XML::NodeList> pList = sch->getElementsByTagName("action");
	for(int i=0; i<pList->length(); ++i) {
		handle_schedule_action(dynamic_cast<Element*>(pList->item(i)), s);
	}

	schedules_.insert(std::make_pair(id,  s));
}

void Configuration::handle_schedule_action(Element* action, Schedule& s)
{
    Action a;
	a.id = action->getAttribute("id");

	if (Element *e = action->getChildElement("at"))
		a.at = boost::lexical_cast<int>(e->innerText());
    else
        a.at = 0;

	if (Element *e = action->getChildElement("command"))
		a.command = e->innerText();

	if (Element *e = action->getChildElement("kill"))
		a.kill = e->getAttribute("id");

    s.actions.push_back(a);
}

void Configuration::handle_setup(Element* setup)
{
    assert(setup);

    Setup s;
    s.host = setup->getAttribute("host");

	if(setups_.count(s.host))
		throw XMLSchemaError("Setup for host " + s.host + " appears more than once");

	if (Element *e = setup->getChildElement("schedule"))
        s.schedule = e->getAttribute("id");

	if (Element *e = setup->getChildElement("results"))
        s.results = e->getAttribute("id");

    if(s.host.empty())
        throw XMLSchemaError("Setup is missing mandatory host attribute");
    if(s.schedule.empty())
        throw XMLSchemaError("Setup is missing mandatory schedule element");
    if(s.results.empty())
        throw XMLSchemaError("Setup is missing mandatory results element");

    setups_.insert(make_pair(s.host, s));
}

Configuration::setups_t const & Configuration::setups() const
{
    return setups_;
}

Configuration::Schedule const & Configuration::schedule(std::string const & id) const
{
    schedules_t::const_iterator i = schedules_.find(id);
    if (i == schedules_.end())
        throw std::runtime_error("Schedule " + id + " is not defined");

    return i->second;
}

Configuration::Host const & Configuration::host(std::string const & id) const
{
    hosts_t::const_iterator i = hosts_.find(id);
    if (i == hosts_.end())
        throw std::runtime_error("Host " + id + " is not defined");

    return i->second;
}

int Configuration::test_duration() const
{
    return test_.duration;
}
