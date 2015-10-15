#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flup.server.fcgi import WSGIServer
from beaker.middleware import SessionMiddleware

import dispatcher

from conf import config

# Configure the SessionMiddleware
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': False,
    'session.use_cookie': True,
    'data_dir': 'data/sessions',
    'session.data_dir': 'data/sessions'
}

if __name__ == "__main__":
    oldmask = os.umask (000)
    wsgi_app = SessionMiddleware(dispatcher.app, session_opts)
    WSGIServer(wsgi_app,bindAddress=config['socket']).run()
    os.umask (oldmask)
