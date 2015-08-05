#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implements the dispatch of requests to correct modules
"""

import os
import logging

logger=None

def init():
    """Initialize stuff
    """
    global logger
    if logger is None:
        # Source: https://docs.python.org/2/howto/logging-cookbook.html
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('{name}.log'.format(name=__name__))
        fh.setLevel(logging.DEBUG)
	formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

def app(environ, start_response):
    """ Main handler
    """
    init()
    script=os.path.basename(environ["SCRIPT_NAME"])
    response=[]
    try:
        module=__import__(script)
        response=module.main(environ)
        start_response('200 OK', [('Content-Type', 'application/javascript;charset=utf-8')])
        logger.info("Script '{0}' called: Responded with {1}".format(script,"200 OK"))
    except ImportError as e: 
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        response.append("Not Found")
        logger.info("Script '{0}' called: Responded with {1}.".format(script,"404 Not Found"))
        if script not in str(e):
            logger.error("Couldn't load {0}. Root Cause: {1}".format(script,e))
        else:
            logger.error(e)

    return(response)

def fake_start_response(x,y):
    """Fake start_response for cases where """
    print "== Response =="
    print x
    print "== Headers =="
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(y)
    print "== Body =="

if __name__ == "__main__":
    print "== Logging errors to {0}.log ==".format(__name__)
    import pprint
    os.environ["SCRIPT_NAME"]='getNodeList'
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(app(os.environ,fake_start_response))
