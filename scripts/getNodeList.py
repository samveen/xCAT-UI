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
                          "-i", "serial,groups,ip,cputype,memory,rack,unit,currstate,status,statustime"
                        ],
                        shell=False, stdout=subprocess.PIPE).stdout

    fields={}
    node=""
    for line in fd: 
        if "=" not in line:
            if node != "":
                if "spare" in fields["node"] and "-ilo" not in fields["node"]:
                    result.append('{{ {0} }}'.format(", ".join(['"{k}": "{v}"'.format(k=k,v=v) for k,v in iter(sorted(fields.iteritems()))])))

            node=line.split(':',2)[1].strip()
            fields={"node":node}
        else:
            key,val=line.strip().split('=',2)
            fields[key]=val

    # Get results and convert to expected json for each row
    ## Expected json form of array of row dicts
    """[
        {
            "node": "",
            "serial": "",
            "groups": "",
            "ip": "",
            "cputype": "",
            "memory": "",
            "rack": "",
            "unit": "",
            "currstate": "",
            "status": "",
            "statustime": ""
        }, ... //no trailing comma
    ]"""
    #for r in c.fetchall():
    #    result.append('{{ {0} }}'.format(", ".join(['"{k}": "{v}"'.format(k=columns[i],v=r[i]) for i in range(len(columns))])))

    # make ''.join(result) a valid json array of rows
    result=",\n`".join(result).split('`')
    result.insert(0,"[\n")
    result.append("]\n")

    # Cleanup
    # return the results
    return result

if __name__ == "__main__":
    import os
    for x in main(os.environ):
        print x,
