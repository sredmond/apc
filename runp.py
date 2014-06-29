#!/usr/bin/env python
from app import app
from OpenSSL import SSL

#Setup an SSL context for encrypting communications
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('/usr/share/menlo/apphysics.menloschool.org.key')
context.use_certificate_file('/usr/share/menlo/apphysics.menloschool.org.crt')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False, ssl_context=context)
