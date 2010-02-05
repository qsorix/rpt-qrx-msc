#include "ssh_connection.h"
#include <libssh/libssh.h>
#include <stdexcept>

namespace QRX {

SshConnection::SshConnection(std::string const& host, std::string const & user)
	: host_(host), user_(user)
{
	session_ = ssh_new();
	if (session_ == NULL) {
		throw std::runtime_error("can't create ssh session");
	}

	if(!user.empty()) {
		if (ssh_options_set(session_, SSH_OPTIONS_USER, user_.c_str()) < 0) {
			ssh_free(session_);
			throw std::runtime_error("can't set user to " + user);
		}
	}

	if(ssh_options_set(session_, SSH_OPTIONS_HOST, host_.c_str()) < 0) {
		ssh_free(session_);
		throw std::runtime_error("can't set host to " + host);
	}

	if(ssh_connect(session_)) {
		ssh_disconnect(session_);
		std::string err = std::string("can't_connect ") + ssh_get_error(session_);
		ssh_free(session_);
		throw std::runtime_error(err);
	}

	if(SSH_AUTH_SUCCESS != ssh_userauth_autopubkey(session_, NULL)) {
		ssh_disconnect(session_);
		std::string err = std::string("can't_connect ") + ssh_get_error(session_);
		ssh_free(session_);
		throw std::runtime_error(err);
	}

}

SshConnection::~SshConnection()
{
	if(session_) {
		ssh_disconnect(session_);
		ssh_free(session_);
		session_ = NULL;
	}
}

}
