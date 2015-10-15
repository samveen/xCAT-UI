#/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module handles requests to change node data.
"""

from conf import config

import cgi
import subprocess

def process_cmd(cmd):
    print cmd
    proc=subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    proc.wait()

def main (environ):
    """ Reads the query string and updates node fields as per values
    """
    command=[ "lsdef",
                  "-t", "node",
                  "-o"
            ]

    required_params=['serial','node','ip','eno1','ens1f0','nicips.ens1f0','osimage']
    required_fields=['serial','mac','ip','nicips.ens1f0']
    verify_fields=['serial','node','ip','eno1','ens1f0']

    params=cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ);
    
    result=[]

    fields={}

        # Check required params
    missing=[]
    for k in required_params:
        if k not in params or not params[k].value:
            missing.append(k)
    if len(missing) > 0:
        # Required params not found
        result.append('"error" : {{"code" : 8, "message" : "Missing required Params: {0}"}}'.format(','.join(missing)))
    else:
        # Required params found

        command.append(params['node'].value)
        fd=subprocess.Popen(command,
                                shell=False, stdout=subprocess.PIPE).stdout
        """
Object name: spare19-a1
    groups=uatprovision,ilo,AllRackA1
    ip=10.18.16.12
    mac=14:58:d0:5b:a1:30!spare32-priv|8c:dc:d4:01:7b:90!spare32-pub
    mac=c4:34:6b:c5:22:c4 (Alternative and a bad one)
    serial=SGH517XNND
"""

        node=""
        # Load node data
        for line in fd: 
            if "=" not in line:
                node=line.split(':',2)[1].strip()
                fields[node]={"node":node}
            else:
                key,sep,val=line.strip().partition('=')
                if key in required_fields:
                    if key in 'mac' and '|' in val:
                        for i in val.split('|'):
                            m,s,n=i.partition('!')
                            fields[node]['eno1' if 'priv' in n else 'ens1f0']=m
                    else:
                        fields[node][key]=val
        fd.close()

        node=params["node"].value
        if node not in fields:
            # Error: node not found
            result.append('"error" : {"code" : 2, "message" : "Node not found"}')
        else: 
            # We're dealing with an existing node
            # Verify fields
            for k in verify_fields:
                if k not in fields[node] or fields[node][k] != params[k].value:
                    print '{0}: {1},{2}'.format(k,fields[node][k],params[node][k].value)
                    result.append('"error" : {{"code" : 16, "message" : "Node data mismatch on {0}."}}'.format(k))
                    break

            # get the osimage version string -> to add as group
            command=["lsdef","-t","osimage","-o","{o}".format(o=params["osimage"].value),"-i","osvers"]
            proc=subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
            proc.wait()
            lines = proc.stdout.readlines()
            osgroup=lines[1].strip().partition('=')[2]

            if len(result) == 0:
                # All checks passed. Do your magic:

                # Change groups to add osgroup
                command=["chdef","-t","node","{n}".format(n=node),"-p","groups={g}".format(g=osgroup)]
                process_cmd(cmd=command)

                # Change osimage and start provision process
                command=["nodeset","{n}".format(n=node),"osimage={osimage}".format(osimage=params["osimage"].value)]
                process_cmd(cmd=command)
                command=["rsetboot","{n}".format(n=node),"net"]
                process_cmd(cmd=command)
                command=["rpower","{n}".format(n=node),"reset"]
                process_cmd(cmd=command)

                result.append('"data": {{ "node" : "{0}", "osimage": "{1}" }}'.format(node,params["osimage"].value))


        ## Expected json form of result
    """{
        "data" : {
            "node": "Node"
            "osimage": "OSImage"
        }  if (success) else 
        "error" : {
            "code" : 0|int,
            "message" : "Cause"
        }
    }"""

    # make ''.join(result) a valid json object
    result=",\n`".join(result).split('`')
    result.insert(0,"{\n")
    result.append("\n}")

    # Cleanup
    # return the results
    return result

if __name__ == "__main__":
    import os
    environ=os.environ
    environ['wsgi.input']=''
    for x in main(environ):
        print x,
