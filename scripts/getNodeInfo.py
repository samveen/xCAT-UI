#/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the code for reading data from the sqlite DB and returning it as json
"""

from conf import config

import cgi
import subprocess

def main (environ):
    """ Reads the DB and returns a json result as a list of strings
    """
    command=[ "lsdef",
                  "-t", "node",
                  "-o"
            ]

    result=[]
    params=cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ);

    if "node" not in params:
        result.append('"msg" : {"status" : "failure", "exception" : "Node not given"}')
    else:
        command.append(params['node'].value)

        # fields: serial,groups,ip,cputype,memory,rack,unit,currstate,status,statustime
        fd=subprocess.Popen(command,
                            shell=False, stdout=subprocess.PIPE).stdout

        """
Object name: spare19-a1
    arch=x86_64
    bmc=spare19-a1-ilo
    bmcpassword=@Frewfyev5
    bmcusername=lzdinfra
    chain=runimage=http://10.18.16.10/install/custom_runimage/glpi_discover.tgz,shell
    cpucount=24
    cputype=Intel(R) Xeon(R) CPU E5-2430 v2 @ 2.50GHz
    currchain=shell
    currstate=shell
    groups=uatprovision,ilo,AllRackA1
    height=1
    initrd=xcat/genesis.fs.x86_64.gz
    ip=10.18.16.12
    kcmdline=quiet xcatd=10.18.16.10:3001 destiny=shell
    kernel=xcat/genesis.kernel.x86_64
    mac=c4:34:6b:c5:22:c4
    memory=32010MB
    mgt=ipmi
    netboot=xnba
    ondiscover=nodediscover
    postbootscripts=otherpkgs
    postscripts=syslog,remoteshell,syncfiles
    rack=A1
    serial=SGH517XNND
    status=booting
    statustime=08-14-2015 20:43:40
    supportedarchs=x86,x86_64
    unit=19
"""
        fields={}
        required_fields=['serial','mac','memory','cputype','bmc','rack','unit','ip','nicips.ens1f0','groups','provmethod']
        node=""
        for line in fd: 
            if "=" not in line:
                node=line.split(':',2)[1].strip()
                fields={"node":node}
            else:
                key,sep,val=line.strip().partition('=')
                if key in required_fields:
                    if key in 'mac':
                        if '|' in val:
                            macs=[]
                            for i in val.split('|'):
                                m,s,n=i.partition('!')
                                macs.append('{{"name": "{n}", "mac": "{m}"}}'.format(n='eno1' if 'priv' in n else 'ens1f0',m=m))
                            fields[key]="[ {0} ]".format(",".join(macs))
                        else:
                            fields[key]='[ {{ "name": "eno1", "mac": "{0}"}} ]'.format(val)
                    elif key in 'groups':
                        fields[key]=val.split(',')[-1]
                    else:
                        fields[key]=val

        # Discover unused spare name    
        newnode=""
        index=1;
        while True:
            newnode="spare{0}".format(index)
            proc=subprocess.Popen(['nodels',newnode], shell=False, stdout=subprocess.PIPE)
            proc.wait()
            lines = proc.stdout.readlines()
            if len(lines) == 0:
                break
            index+=1;

        if "node" in fields:
            fields['newnode']=newnode
            result.append('"msg" : {"status" : "success", "exception" : ""}')
            result.append('"node": {{ {0} }}'.format(", ".join(['"{k}": "{v}"'.format(k=k,v=v) if 'mac' not in k else '"{k}": {v}'.format(k=k,v=v) for k,v in iter(sorted(fields.iteritems()))])))
        else: 
            result.append('"msg" : {"status" : "failure", "exception" : "Node not found"}')


        # Get results and convert to expected json for each row
        ## Expected json form of array of row dicts
        """{
            "node" : {
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
            }, 
            "msg" : { "status" : "success|failure", exception : "Cause" } //no trailing comma
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
    environ=os.environ
    environ['wsgi.input']=''
    for x in main(environ):
        print x,
