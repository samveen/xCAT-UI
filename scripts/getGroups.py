#/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module returns the groups matching the display group criteria
"""

from conf import config

import re

import subprocess
import itertools

def main (environ):
    """ Reads the groups and returns a json result as a list of strings
    """

    # Auth check
    session=environ['beaker.session']
    if 'user_id' not in session:
        # Authentication Failed
        return '{"error": { "code": -512, "message": "Not Authenticated"}}'

    pattern = None
    if 'DisplayGroups' in config['getGroups']:
        pattern = re.compile(config['getGroups']['DisplayGroups'])

    result=[]

    # fields: serial,groups,ip,cputype,memory,rack,unit,currstate,status,statustime
    with subprocess.Popen([ "lsdef", "-t", "group", "-i", "members" ], shell=False, stdout=subprocess.PIPE).stdout as fd:
        """ OUTPUT: 
        Object name: kvm
            members=cacti,cacti1,mta1,netmon1,netproxy1
        """
        for gline, mline in itertools.izip(fd,fd):
            name=gline.strip().split(':',2)[1].strip()
            if 'DisplayGroups' not in config['getGroups'] or pattern.match(name):
                count=len(mline.strip().split('=',2)[1].strip().split(','))
                result.append('{{"name":"{n}","count":"{c}"}}'.format(n=name,c=count))
        result=['"data":{{\n"groups" : [ {0} ]'.format(', '.join(result))]
        # result.append(' : [ {0} ]'.format(", ".join(['"{i}"'.format(i=i) for i in groups])))
        result.append('"msg" : {"status" : "success"}\n}')

    # Get results and convert to expected json for each row
    ## Expected json form of array of row dicts
    """{
          "data" : {
            "groups" : [
                     { "name": "G1" : "count" : "c1" },
                     { "name": "G2" : "count" : "c2" }, ...
            ],
            "msg" : { "status" : "success|failure", exception : "Cause" }
          }
    }"""
    #for r in c.fetchall():
    #    result.append('{{ {0} }}'.format(", ".join(['"{k}": "{v}"'.format(k=columns[i],v=r[i]) for i in range(len(columns))])))
    if len(result) == 0:
        result = ['"error": {"code": 1, "message": "No matching groups found"}']

    # make ''.join(result) a valid json array of rows
    result=",\n`".join(result).split('`')
    result.insert(0,"{\n")
    result.append("\n}")

    # Cleanup
    # return the results
    return result

if __name__ == "__main__":
    import os
    for x in main(os.environ):
        print x,
