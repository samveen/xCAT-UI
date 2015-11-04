# Requirements
* Python (Server side code)
** Python-flup (WSGI container)
** Python-pam (Auth)
** Python-beaker (Session management)
* Nginx (Reverse proxy)
* xCAT (to actually do something)

# Create user xcatui
```
[root@xcatmn]# useradd -c 'xCAT WebUI user' -d /opt/xCAT-UI -g nginx  -m -N -s /bin/bash xcatui
```

# xCAT Permissions
```
[root@xcatmn]# cat xcatuiperms.xstanza
7:
    objtype=policy
    commands=lsdef,nodels,chdef,makedhcp,makedns,makehosts,nodeset,rsetboot,rpower,nodestat,makeconservercf
    name=xcatui
    rule=allow
[root@xcatmn]# cat xcatuiperms.xstanza | mkdef -z
[root@xcatmn]# /opt/xcat/share/xcat/scripts/setup-local-client.sh xcatui
```
# Set up things
Log in as the xcatui user and setup things:
```
git clone "git@github.com:samveen/xCAT-UI.git" .
chmod g+x .
```

# Setup nginx:
* Change default listening port from 80 to 8080 (as 80 is used by apacha+xcat)
* Create a link to `~xcatui/nginx_conf/xCAT-UI.conf` in `/etc/nginx/default.d/`
* Enable and start nginx

# Start the Python webservice(as user xcatui):
```
screen -S webservice -d -m bash -c 'cd ~/scripts && make run'
```

# Enjoy
* We're good
