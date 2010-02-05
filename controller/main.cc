#include <Poco/DOM/Document.h>
#include <Poco/DOM/DOMParser.h>
#include <Poco/AutoPtr.h>
#include <Poco/Net/DialogSocket.h>
#include <Poco/Net/SocketAddress.h>

#include <boost/foreach.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>

#include <iostream>
#include <sstream>
#include <ctime>

#include "configuration.h"

std::list<std::string> serialize_schedule(Configuration::Schedule const & s)
{
	std::list<std::string> ret;

	BOOST_FOREACH(Configuration::Action const &a, s.actions) {
		std::stringstream str;
		str << a.at << ": ";
		if(!a.id.empty())
			str << "{" << a.id << "} ";
		if(!a.command.empty())
			str << a.command;
		else if(!a.kill.empty())
			str << "kill {" << a.kill << "}";

		ret.push_back(str.str());
	}

	return ret;
}

struct ProtocolError : public std::runtime_error
{
	ProtocolError(std::string const& msg) : std::runtime_error(msg) {}
};

Poco::Net::DialogSocket& operator<<(Poco::Net::DialogSocket &ds, std::string const & message)
{
	std::string ans;
	ds.sendMessage(message);
	int ret = ds.receiveStatusMessage(ans);
	if (ret == 0) {
		throw ProtocolError("Connection closed by peer");
	}
	if (ret != 200) {
		throw ProtocolError("Protocol error, response: " + ans);
	}
	return ds;
}

Poco::Net::DialogSocket& operator<<(Poco::Net::DialogSocket &ds, char const* message)
{
	return ds << std::string(message);
}


int main(int argc, char** argv)
{
	if(argc!=2) {
		std::cerr << "podaj uri do pliku konfiguracyjnego (file:///)" << std::endl;
		return 1;
	}

	Poco::XML::DOMParser parser;

	Poco::AutoPtr<Poco::XML::Document> pDoc = parser.parse(argv[1]);
	Configuration config(*pDoc);

	int test_number = std::time(NULL);

	std::map<std::string, std::list<std::string>  > setups;
	std::map<std::string, Poco::Net::DialogSocket* > sockets;

	std::cout << " --- configuring hosts --- " << std::endl;

	BOOST_FOREACH(Configuration::setups_t::const_iterator::value_type i, config.setups()) {
		std::list<std::string> sch = serialize_schedule(config.schedule(i.second.schedule));
		std::list<std::string> res = serialize_schedule(config.schedule(i.second.results));

		std::list<std::string>& cmds = setups[i.first];
		cmds.push_back("test " + boost::lexical_cast<std::string>(test_number));

		cmds.push_back("schedule " + boost::lexical_cast<std::string>(sch.size()));
		cmds.insert(cmds.end(), sch.begin(), sch.end());

		cmds.push_back("cmds " + boost::lexical_cast<std::string>(res.size()));
		cmds.insert(cmds.end(), res.begin(), res.end());

		cmds.push_back("duration " + boost::lexical_cast<std::string>(config.test_duration()));

		Configuration::Host const & host = config.host(i.first);
		std::string conn_str;
		if(!host.ip.empty())
			conn_str = host.ip;
		else
			conn_str = host.name;
		conn_str += ":" + boost::lexical_cast<std::string>(host.port);

		std::cout << "connecting with: " << conn_str << std::endl;

		sockets[i.first] = new Poco::Net::DialogSocket;
		sockets[i.first]->connect(Poco::Net::SocketAddress(conn_str));

		BOOST_FOREACH(std::string cmd, cmds) {
			(*sockets[i.first]) << cmd;
		}
	}

	using namespace boost::posix_time;
	ptime start = second_clock::universal_time() + seconds(5);
	std::string start_str = boost::posix_time::to_iso_extended_string(start);
	start_str[10]=' '; // FIXME - ugly

	BOOST_FOREACH(Configuration::setups_t::const_iterator::value_type i, config.setups()) {
		std::list<std::string>& cmds = setups[i.first];
		(*sockets[i.first]) << ("start " + start_str);
		(*sockets[i.first]) << "end";
		sockets[i.first]->close();
		delete sockets[i.first];
	}

	std::cout << " --- waiting for the test to finish --- " << std::endl;
	usleep(((config.test_duration()+5)) * 1000000);
	std::cout << " --- gathering results --- " << std::endl;

	BOOST_FOREACH(Configuration::setups_t::const_iterator::value_type i, config.setups()) {
		Configuration::Host const & host = config.host(i.first);
		std::string conn_str;
		if(!host.ip.empty())
			conn_str = host.ip;
		else
			conn_str = host.name;
		conn_str += ":" + boost::lexical_cast<std::string>(host.port);

		std::cout << "\n\nconnecting with: " << conn_str << std::endl;

		sockets[i.first] = new Poco::Net::DialogSocket;
		sockets[i.first]->connect(Poco::Net::SocketAddress(conn_str));
		
		(*sockets[i.first]) << ("results " + boost::lexical_cast<std::string>(test_number));

		std::string line;
		while((*sockets[i.first]).receiveMessage(line)) {
			std::cout << line << std::endl;
		}

		sockets[i.first]->close();
		delete sockets[i.first];
	}

	return 0;
}
