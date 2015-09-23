#/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module handles requests to change node data.
"""

from conf import config

import cgi
import subprocess

def process_cmd(cmd):
    print cmd
#    fd=subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE).stdout
#    for line in fd: 
#        pass

def main (environ):
    """ Reads the query string and updates node fields as per values
    """
    command=[ "lsdef",
                  "-t", "node",
                  "-o"
            ]

    required_params=['serial','node','ip','eno1','ens1f0','groups']
    required_fields=['serial','mac','ip','nicips.ens1f0','groups']
    verify_fields=['serial','node','ip','eno1','ens1f0','groups']

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
        # Load node data and newnode data (in case newnode already exists)
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
        newnode="spareXYZ"
        if newnode in fields:
            # Target Node found
            result.append('"error" : {"code" : 32, "message" : "Target node already exists"}')
        elif node not in fields:
            # Error: node not found
            result.append('"error" : {"code" : 2, "message" : "Node not found"}')
        elif "spare" in node:
            # Error: Node found, but a spare
            result.append('"error" : {"code" : 4, "message" : "Node already a spare node"}')
        else: 
            # We're dealing with an existing non-spare node
            # Verify fields
            for k in verify_fields:
                if k not in fields[node] or params[k].value not in fields[node][k]:
                    print '{0}: {1},{2}'.format(k,fields[node][k],params[node][k].value)
                    result.append('"error" : {{"code" : 16, "message" : "Node data mismatch on {0}."}}'.format(k))
                    break

            # Check if new IP assignment, and if new IP is already assigned
            if len(result) == 0 and params["nicips.ens1f0"].value != fields[node]["nicips.ens1f0"]:
                command=[ "nodels", "nics.nicips=~!{ip}$".format(ip=params["nicips.ens1f0"].value) ]
                fd=subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout
                line=fd.readline().strip()
                if line:
                    result.append('"error" : {{"code" : 32, "message" : "{ip} already assigned to {n}."}}'.format(ip=params["nicips.ens1f0"].value,n=line))

            if len(result) == 0:
                # All checks passed. Do your magic:

                # Remove dhcp,dns,hosts entries
                command=["makedhcp","-d","{0},{0}-ilo".format(node)]
                process_cmd(cmd=command)
                command=["makedns","-d","{0},{0}-ilo".format(node)]
                process_cmd(cmd=command)
                command=["makehosts","-d","{0},{0}-ilo".format(node)]
                process_cmd(cmd=command)

                # Rename node and ilo
                command=["chdef","-t","node","-o","{o}".format(o=node),"-n","{n}".format(n=newnode)]
                process_cmd(cmd=command)
                command=["chdef","-t","node","-o","{o}-ilo".format(o=node),"-n","{n}-ilo".format(n=newnode)]
                process_cmd(cmd=command)

                # Change groups to remove remove usage group and add uatprovision
                command=["chdef","-t","node","{n}".format(n=newnode),"-m","groups={g}".format(g=params["groups"].value)]
                process_cmd(cmd=command)
                command=["chdef","-t","node","{n}".format(n=newnode),"-p","groups=uatprovision"]
                process_cmd(cmd=command)

                # Change mac-associated names
                mac="{eno1}!{n}-priv|{ens1f0}!{n}-pub".format(n=newnode,eno1=params["eno1"].value,ens1f0=params["ens1f0"].value)
                command=["chdef","-t","node","{n}".format(n=newnode),"mac={m}".format(m=mac)]
                process_cmd(cmd=command)

                # Remake dhcp,dns,hosts entries
                if not params["nicips.ens1f0"].value == fields[node]["nicips.ens1f0"]:
                    command=["chdef","-t","node","{n}".format(n=newnode),"nicips.ens1f0={newip}".format(newip=params["nicips.ens1f0"].value)]
                    process_cmd(cmd=command)

                # Remake dhcp,dns,hosts entries
                command=["makehosts","{0},{0}-ilo".format(newnode)]
                process_cmd(cmd=command)
                command=["makedns","{0},{0}-ilo".format(newnode)]
                process_cmd(cmd=command)
                command=["makedhcp","{0},{0}-ilo".format(newnode)]
                process_cmd(cmd=command)

                # Change osimage and start provision process
                command=["nodeset","{n}".format(n=newnode),"osimage={d}".format(d=config['decommNode']['osimage'])]
                process_cmd(cmd=command)
                command=["rsetboot","{n}".format(n=newnode),"net"]
                process_cmd(cmd=command)
                command=["rpower","{n}".format(n=newnode),"up"]
                process_cmd(cmd=command)
                command=["rpower","{n}".format(n=newnode),"reset"]
                process_cmd(cmd=command)

                result.append('"data": {{ "node":" {0}", "updated" : "{1}" }}'.format(node,newnode))


        ## Expected json form of result
    """{
        "data" : {
            "updated": "BrandNewNode"
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
    print "Result: {0}".format(result)
    return result

if __name__ == "__main__":
    import os
    environ=os.environ
    environ['wsgi.input']=''
    for x in main(environ):
        print x,
