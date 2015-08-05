#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flup.server.fcgi import WSGIServer
import dispatcher

from conf import config

if __name__ == "__main__":
    oldmask = os.umask (000)
    WSGIServer(dispatcher.app,bindAddress=config['socket']).run()
    os.umask (oldmask)
