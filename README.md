Consul Nomad Cluster
====================

This repo is a lab environment to test Consul and Nomad. Keep in mind, no security measurements have been taken, it's purely for lab work.

The provisioning is managed by Ansible. This lab has been working for me on both Linux Ubuntu Trusty64 KVM Virtualization and Mac OSX Virtualbox Virtualization.
Included are Ansible roles to spin up a XtraDB cluster and MeteorJS apps, just to have something to start with.

Here are the dependencies for the host systems used:

Mac OSX 10.11.3 El Capitan:
---------------------------
* >= 16 GB RAM
* >= ansible 2.0.1.0
* >= vagrant 1.8.1
* >= Virtualbox 4.3.34 - Although I tried 5, I reverted back to 4.3.34 because I experienced inconsistencies with Vagrant. If I remember, it had to do with network card incompatibilities. I don't think it affects this project, but haven't verified yet.


Linux Ubuntu 14.04 LTS
----------------------
* 16 GB RAM
* ansible 2.0.1.0
* vagrant 1.8.1
* kvm

Vagrant Libvirt and KVM
-----------------------

Apt Package dependencies for Libvirt and KVM on the host machine:
```
apt-get install libxslt-dev libxml2-dev libvirt-dev zlib1g-dev ruby-dev qemu-kvm libvirt-bin bridge-utils virt-manager qemu-system
```

If you have a trusty64 Ubuntu 14.04 vagrant box for libvirt or kvm, you can probably use it. I didn't have one, so I vagrant mutated the "ubuntu/trusty64" box using this project:
```
https://github.com/sciurus/vagrant-mutate
```

Here's how to mutate the "ubuntu/trusty64" standard box. Download the Vagrant installer deb package: [here](https://releases.hashicorp.com/vagrant/1.8.1/vagrant_1.8.1_x86_64.deb).
```
dpkg -i vagrant_1.8.1_x86_64.deb
```

It turns out at the time, I didn't have the libvirt-dev package installed on the host machine for the vagrant-libvirt plugin. It's included in the host's apt dependencies above:
```
apt-get -y install libvirt-dev # I Didn't have this package
vagrant plugin install vagrant-libvirt
```

Now the installation works with the libvirt-dev package in place.
```
vagrant plugin install vagrant-libvirt
```

###Notice in case vagrant-libvirt installation fails:
For some reason, the vagrant-libvirt installation complained again, and I read a Git issue which solved the installation problem by reinstalling the Fog library Vagrant plugin with a specific version - fog-libvirt [https://github.com/fog/fog-libvirt](https://github.com/fog/fog-libvirt) I need to update this doc with the source.

```
vagrant plugin install --plugin-version 0.0.3 fog-libvirt
```

Vagrant Mutate Box
------------------

I needed a vagrant box, so I downloaded and named it "trusty64":
```
vagrant box add trusty64 https://vagrantcloud.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box
```

And then mutated trusty64 for libvirt:
```
vagrant mutate trusty64 libvirt
```

I quickly checked the qemu user existed and the libvirt connection with these commands:

```
cat /etc/group
cat /etc/passwd
virsh -c qemu:///system list
virsh list --all
```

Ansible
-------

I used the standard Ansible installation method, and I'm using defaults. I didn't create an ansible.cfg to place ssh key locations or inventory dirs. I'm using the playbook dir as the base path.

Install PIP if you dont have it, or follow a different Ansible installation:

```
apt-get install -y python-pip
```

```
pip install --upgrade
apt-get install software-properties-common
apt-add-repository ppa:ansible/ansible
apt-get update
apt-get install ansible
ansible --version
```


Vagrantfile
-----------

The Vagrantfile has been made to be scalable to a certain degree. In theory, just adjusting the NUM_XXX will be enough to create as many VMs as the IP generation would allow in the Vagrantfile...so dozens at the moment. Currently, it's setup with 3 consul servers and 3 consul clients, as described in Ansible terms below.

```
consul[1:3].cluster
client[1:3].cluster
```


Getting Started:
================

Ensure that you have the above dependencies satisfied.
Spin up the 6 node cluster, in two steps to prevent a race condition between the guest network interfaces and ansible ssh
```
vagrant up --no-provision
vagrant provision
```

The ```vagrant up --no-provision``` command will create 6 nodes. The ```vagrant provision``` will run the Ansible playbook. See details below.

Ansible Playbook
================

IMHO, this playbook kind of breaks Ansible best practices, but it's easier for me to see all the arguments provided to the role. Yes, there are some variables that should be set in production and kept in a vault, but this is a lab for spinning up infrastructure. I'm not planning on building inventory files, since vagrant is dynamically handling that. I create an inventory file, but Vagrant doesn't use it. In a production setting, you would want to create a priveleged user to manage these ssh connections.

This playbook creates a 3 node Consul/Nomad server cluster and a 3 node Consul/Nomad client cluster.

Upstart Init scripts have been created to manage the following consul and nomad agent command execution. These init scripts are simple, and have conditions that depend on the 'ansible_eth1' interface to be available. 


On clients:
-----------
```
[start|stop|restart|status] consul_client
[start|stop|restart|status] nomad_client
```


On servers:
-----------
```
[start|stop|restart|status] consul_server
[start|stop|restart|status] nomad_server
```

Manual Consul Agent Reference
-----------------------------

If running the commands manually, you can bootstrap a cluster like so (with the Consul UI available on each host):

On each node run it's respective consul agent command
```
sudo consul agent -server -advertise="172.136.9.56" -data-dir="/tmp/consul" -ui -bootstrap-expect 3 -ui-dir /opt/consul/ -client="127.0.0.1"
sudo consul agent -server -advertise="172.136.9.57" -data-dir="/tmp/consul" -ui -bootstrap-expect 3 -ui-dir /opt/consul/ -client="127.0.0.1"
sudo consul agent -server -advertise="172.136.9.58" -data-dir="/tmp/consul" -ui -bootstrap-expect 3 -ui-dir /opt/consul/ -client="127.0.0.1"
```
Then on any node manually join the cluster:
```
sudo consul join 172.136.9.56 172.136.9.57 172.136.9.58
```

Check Cluster:
--------------
```
consul info
consul members
```


Check Logs:
-----------
```
tail -f /var/log/upstart/consul_server.log 
```

Check the UIs:
--------------
Each server host has been port forwarded, so guest 1 8500-> host 8501, and guest 2 8500 -> host 8502...
http://localhost:8501/ui
http://localhost:8502/ui

Check the API:
--------------
```
curl http://172.136.9.56:8500/v1/catalog/nodes
curl http://172.136.9.57:8500/v1/catalog/nodes
curl http://172.136.9.58:8500/v1/catalog/nodes
...
```

Consul Checks
-------------

On the servers you'll find: /opt/consul/server/config.json 
On the clients you'll find: /opt/consul/client/config.json

There are several checks I've included for each. Consul has a similar way of managing checks to Nagios, so included are basic API type Nagios style checks.
In particular, there is a helpful plugin written by Guillaume Coré to monitor XtraDB:
```
https://github.com/fridim/nagios-plugin-check_galera_cluster
```


Another helpful project found the templates directory for integration with HAproxy is by:
```
David Busby, Percona Ireland Ltd, found here: https://github.com/Oneiroi/clustercheck
```

There is a basic JSON check for the Druid.io API, as a placeholder test.


Ansible commands for cluster management:
========================================

Have a look in the role /defaults folder, they show the role's parameters you can override in your group_vars/host_vars files should you choose to store them that way. Take a look at the playbooks role parameters and see what's set. The biggest factor is that the 'eth1' is the main shared subnet interface for which Raft consensus protocols can communicate.

You'll find several filter_plugins creating the dynamic formatting of group vars and hostvars

Few Ansible key variables in this: 
```
nomad_server: True|False - sets the inventory to nomad server or client, in which case you need to provide as well, the defaults probably wont work."
consul_server: True|False
```

The following Ansible commands are using the default insecure_private_key provided by Vagrant.


Stop the Consul Servers:
------------------------
Note if these fail from UNREACHABLE, you may have to delete the old entry from the known hosts file:

```
ssh-keygen -R 172.136.9.56
```
...and remove the rest


```
ansible all -i 172.136.9.56,172.136.9.57,172.136.9.58, -m shell -a "/sbin/stop consul_server" --private-key ~/.vagrant.d/insecure_private_key -u vagrant -b
```

Restart the Consul Servers:
-------------------------
```
ansible all -i 172.136.9.56,172.136.9.57,172.136.9.58, -m shell -a "/sbin/restart consul_server" --private-key ~/.vagrant.d/insecure_private_key -u vagrant -b
```

Consul Clients
==============

Stop the Consul Clients:
------------------------
```
ansible all -i 172.136.9.106,172.136.9.107,172.136.9.108, -m shell -a "/sbin/stop consul_client" --private-key ~/.vagrant.d/insecure_private_key -u vagrant -b
```

Start the Consul Clients:
-------------------------
```
ansible all -i 172.136.9.106,172.136.9.107,172.136.9.108, -m shell -a "/sbin/restart consul_client" --private-key ~/.vagrant.d/insecure_private_key -u vagrant -b

```

Consul DNS:
===========

Structure of the dns:
```
[tag.]<service>.service[.datacenter].<domain>
```

On any server query DNS for a node:

```
dig @127.0.0.1 -p 8600 consul1.node.consul ANY
dig @127.0.0.1 -p 8600 consul2.node.consul ANY
```

Meteor App
==========

I wanted a modern web application to test, so there is a simple meteor Ansible role included. I've not added any nomad jobs or consul checks yet.

```
cd /opt/meteor/meteor_app/
```

to run the dev server listening on port 3000:
```
meteor
```

Installs an upstart script that needs work (/etc/init/meteor_app.conf). The proper ENV variables need to be set:

Environment Variables used by Meteor:
-------------------------------------
```
BIND IP: bind to a specific IP address (optional)
DISABLE WEBSOCKETS: Set to 1 to disable trying websockets first before falling back to sockjs emulation
HTTP_FORWARDED_COUNT: set this with the number of proxies Meteor is running behind (optional)
MAIL_URL: how Meteor will send email, SMTP settings etc. (required to send email)
METEOR_SETTINGS: various runtime settings, see link (optional)
MONGO_OPLOG_URL: URL for Mongo (optional)
MONGO_URL: URL for connecting to Mongo (required in production)
NODE_ENV: not required by Meteor but set to 'PRODUCTION' by most node.js Category:PaaS_providers.
NODE_OPTIONS: Used in development (i.e. via Meteor-run) to pass additional options to node (like --debug). Optional.
PACKAGE_DIRS: If you wish to add packages outside of your application folder structure, set it to directory containing the packages. If more than one location, use colon to delimit the list. (optional)
PORT: What port to listen on (optional, defaults to 3000)
ROOT_URL: Default URL for how your app should be access (required on production)
```

Nomad
=====

to avoid writing the address flag on every command:
```
export NOMAD_ADDR=http://172.136.9.56:4646
```

Similar to Consul, Nomad is set up with an upstart script depending on the install type.
```
cat /etc/init/nomad_server
cat /etc/init/nomad_client
```
Check the status of the nomad agent:
```
nomad agent-info -address=http://172.136.9.56:4646
```

Check the node status:
```
nomad node-status -address=http://172.136.9.56:4646
```

Check the cluster:
```
nomad server-members -address=http://172.136.9.56:4646
```
XtraDB
======

This role installs XtraDB MySQL 5.6 on the client hosts. Secondly, I'm working on the bootstrap process. Most of the logic is there. I believe the Ansible tasks included here (roles/xtradb/state.yml) that manage the bootstrap exit too fast. and dont allow the cluster to form. To manually form the cluster:

Stop all nodes:
```
/etc/init.d/mysql stop
```

From your leader mysql node (client1.cluster in this case): 

Ensure that the my.cnf variable (Once the cluster is up, you'll want to set it to the full list of ip addresses):
```
wsrep_cluster_address = gcomm://
```

Then you start the bootstrap process. You'll bring up a cluster of 1, then add the rest of the nodes one by one.
```
/etc/init.d/mysql bootstrap-pxc
```

Then login to mysql, check the cluster stats:
```
mysql> show status like 'wsrep%';
```

This should show something similar to the following (cluster of 1):
```
mysql> show status like 'wsrep%';
+----------------------------+--------------------------------------+
| Variable_name              | Value                                |
+----------------------------+--------------------------------------+
| wsrep_local_state_uuid     | b598af3e-ace3-11e2-0800-3e90eb9cd5d3 |
...
| wsrep_local_state          | 4                                    |
| wsrep_local_state_comment  | Synced                               |
...
| wsrep_cluster_size         | 1                                    |
| wsrep_cluster_status       | Primary                              |
| wsrep_connected            | ON                                   |
...
| wsrep_ready                | ON                                   |
+----------------------------+--------------------------------------+
40 rows in set (0.01 sec)
```

Start the other nodes, 1-by-1:
```
/etc/init.d/mysql start
```

Run the same status check on these nodes and verify similar output:
```
mysql> show status like 'wsrep%';
```

Now if your cluster is healthy, log back into the Consul UI, you'll hopefully see all passing health checks on the xtradb service:)

Todo:
=====

* Convert Go install to idempotent role
* Integrate a Docker Registry Cluster Role [https://github.com/chrisjalinsky/docker-registry-cluster](https://github.com/chrisjalinsky/docker-registry-cluster)
* Add Docker Nomad Jobs
* Add Nomad Exec and Raw Exec Jobs
* Add Rkt Nomad Jobs
* Get the new user generated to own the consul and nomad processes
* More docs

Any help or advice or suggestions are welcome.