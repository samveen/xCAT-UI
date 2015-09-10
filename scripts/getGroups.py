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
                          "-t", "node",
                          "-i", "groups"
                        ],
                        shell=False, stdout=subprocess.PIPE).stdout
    counts = {}
    for line in fd: 
        if "=" in line:
            key,val=line.strip().split('=',2)
            for i in val.split(","):
                if 'DisplayGroups' not in config['getGroups'] or i in config['getGroups']['DisplayGroups']:
                    if i in counts:
                        counts[i]=counts[i]+1
                    else:
                        counts[i]=1
    result.append('"groups" : [ {0} ]'.format(", ".join(['{{"name":"{k}","count":"{v}"}}'.format(k=k,v=v) for k,v in iter(sorted(counts.iteritems()))])))
    # result.append(' : [ {0} ]'.format(", ".join(['"{i}"'.format(i=i) for i in groups])))
    result.append('"msg" : {"status" : "success"}')

    # Get results and convert to expected json for each row
    ## Expected json form of array of row dicts
    """{
        "groups" : [
                     { "name": "G1" : "count" : "c1" }
                     { "name": "G2" : "count" : "c2" }
        ],
        "msg" : { "status" : "success|failure", exception : "Cause" }
    }"""
    #for r in c.fetchall():
    #    result.append('{{ {0} }}'.format(", ".join(['"{k}": "{v}"'.format(k=columns[i],v=r[i]) for i in range(len(columns))])))

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
