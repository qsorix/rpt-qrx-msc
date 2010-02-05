#ifndef QRX_CONFIGURATION_H
#define QRX_CONFIGURATION_H

#include <Poco/DOM/Document.h>
#include <stdexcept>
#include <map>

struct XMLSchemaError : public std::runtime_error
{
	XMLSchemaError(std::string const& msg) : std::runtime_error(msg) {}
};

class Configuration
{
public:
	struct Host {
		std::string ip;
		std::string name;
		int         port;
	};

    struct Test {
        int duration;
    };

    struct Action {
        std::string id;
        int         at;
        std::string command;
        std::string kill;
    };

    struct Schedule {
        std::list<Action> actions;
    };

    struct Setup {
        std::string host;
        std::string schedule;
        std::string results;
    };

    typedef std::map<std::string, Host>     hosts_t;
    typedef std::map<std::string, Schedule> schedules_t;
    typedef std::map<std::string, Setup>    setups_t;

private:
	hosts_t     hosts_;
    schedules_t schedules_;
    setups_t    setups_;
    Test        test_;

private:
	void handle_hosts(Poco::XML::Element* hosts);
	void handle_host(Poco::XML::Element* host);
	void handle_test(Poco::XML::Element* host);
	void handle_schedule(Poco::XML::Element* host);
    void handle_schedule_action(Poco::XML::Element* action, Schedule& s);
	void handle_setup(Poco::XML::Element* setup);

public:

	Configuration(Poco::XML::Document const & doc);

    setups_t const & setups() const;
    Schedule const & schedule(std::string const & id) const;
    Host     const & host(std::string const & id) const;

    int test_duration() const;

};

#endif
