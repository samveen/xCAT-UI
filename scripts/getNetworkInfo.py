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

    netfields="net,mask"
    # fields: serial,groups,ip,cputype,memory,rack,unit,currstate,status,statustime
    fd=subprocess.Popen([ "lsdef",
                          "-t", "network",
                          "-i", netfields
                        ],
                        shell=False, stdout=subprocess.PIPE).stdout
    nets = {}
    for line in fd: 
        if "=" not in line:
            ign1,ign2,netname=line.partition(':')
            netname=netname.strip()
            nets[netname]={}
        else:
            key,ign,val=line.strip().partition('=')
            nets[netname][key]=val
    
    for n in sorted(nets.keys()):
        result.append('{{ "name": "{0}", {1} }}'.format(n,", ".join(['"{k}": "{v}"'.format(k=k,v=nets[n][k]) for k in (netfields.split(','))])))

    # Get results and convert to expected json for each row
    ## Expected json form of array of row dicts
    """{
        "data": { 
            "nets": [ { "net": "x", ...}, ... ]
        }
    }"""

    # make ''.join(result) a valid json array of rows
    result=",\n`".join(result).split('`')
    result.insert(0,"\"nets\": [\n")
    result.append("]\n")
    result.insert(0,"\"data\": {\n")
    result.append("}\n")
    result.insert(0,"{\n")
    result.append("}\n")

    # Cleanup
    # return the results
    return result

if __name__ == "__main__":
    import os
    for x in main(os.environ):
        print x,
