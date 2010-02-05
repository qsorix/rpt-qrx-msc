#ifndef QRX_SSH_CONNECTION_H
#define QRX_SSH_CONNECTION_H

#include <string>
#include <libssh/libssh.h>

namespace QRX {

class SshConnection {
	std::string host_;
	std::string user_;

	ssh_session session_;

public:
	SshConnection(std::string const & host, std::string const & user);
	~SshConnection();

};

}

#endif
