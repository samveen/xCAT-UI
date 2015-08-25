#/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the code for reading data from the sqlite DB and returning it as json
"""

from conf import config

import subprocess

def main (environ):
    """ Reads the DB and returns a json result as a list of strings
    """

    result=[]

    # fields: serial,groups,ip,cputype,memory,rack,unit,currstate,status,statustime
    fd=subprocess.Popen([ "lsdef",
                          "-t", "osimage"
                        ],
                        shell=False, stdout=subprocess.PIPE).stdout
    osimages = []
    for line in fd: 
        osimages.append(line.replace('(osimage)','').strip())
    if len(osimages) > 0:
        result.append('"msg" : {"status" : "success"}')
        result.append('"osimages" : [ {0} ]'.format(", ".join(['"{i}"'.format(i=i) for i in sorted(osimages)])))
    else:
        result.append('"msg" : {"status" : "failure", "exception": "No osimages found"}')

    # Get results and convert to expected json for each row
    ## Expected json form of array of row dicts
    """{
        "msg" : { "status" : "success|failure", exception : "Cause" }
        "osimages" : [ "image1", "image2", ... ],
    }"""

    # make ''.join(result) a valid json array of rows
    result=",\n`".join(result).split('`')
    result.insert(0,"{\n")
    result.append("}\n")

    # Cleanup
    # return the results
    return result

if __name__ == "__main__":
    import os
    for x in main(os.environ):
        print x,
