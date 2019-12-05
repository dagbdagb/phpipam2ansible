# phpIPAM dynamic inventory script for ansible


## What is this?
It is the 'missing link' between [phpIPAM](https://github.com/phpipam/phpipam) and [ansible](https://github.com/ansible/ansible). It allows ansible to pull hosts and groups from phpIPAM. If you are looking at ansible and wonder what a 'dynamic inventory' is, then this script is what you need if you use phpIPAM. It is also an embarassingly simple piece of python which I held off writing for far too long.


## What is this not?
This is not an introduction to ansible, dynamic inventories, or phpIPAM. And it is likely a bare minimum for a dynamic inventory script. Feel free to fork and improve. In particular, this script does not do nested groups. It is not required, and I solved this need differently. (See below.)


## How to use it
The script expects that you have a .my.cnf in your home directory, with credentials allowing you to access the phpIPAM database, under a [phpipamro] stanza. I suggest creating a read-only dbuser for this purpose. See below for further info.

The script is primarily meant to be used by ansible, but it can be run by the user (you) with the --groups option, to list the groups. Out of the box, each device type is a group. See below for extending this.


Some of the binaries in the ansible suite of tools take an '-i fooo' argument. 'fooo' can be a static inventory file, formatted according to the ansible documentation. Or it can be a dynamic inventory script, like this.

    ansible all -i phpipam2ansible.py --list-hosts

Rather than typing all that on every invocation of an ansible command, you can set the 'inventory' variable in ansible.cfg to point at this script.

    ansible all --list-hosts

But the really cool guys and gals combine static and dynamic inventories. Now you set the 'inventory' variable in ansible.cfg to point at directory. Ansible will expect executables in this directory to take a '--list' option and produce a chunk of JSON output conforming to what ansible expects. Non-executable files are parsed as regular static inventory files.

I use static files to create my nested groups, as well as keeping some dummy hosts I use for other purposes.

```
$ cat inventory/subgroups
[group1_in_ipam]

[group2_in_ipam]

[master_group_not_in_ipam:children]
group1_in_ipam
group2_in_ipam
```

(Unsure if ansible permits underscores in groupnames, but you get the idea.) 
[This](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html#common-patterns) is a useful link for learning how to really make use of groups.


## Creating .my.cnf
This should get you started:

```
$ cat .my.cnf
[phpipam]
user=phpipamro
password=phpipamropassword
database=phpipam
host=phpipamhost

phpipamhost$ mysql -u dbadminuser -p
MariaDB [(none)]> grant select on phpipam.* to 'phpipamro'@'ansiblehost' identified by 'phpipamropassword';
MariaDB [(none)]> flush privileges;
MariaDB [(none)]> \q
```


## Modifying the script
You can extend the script however you like to create as many groups you like, based on whatever attribute you want.
To do that, modify the 'queries' list around line 42 or so. Refer to the comments in the script as well.


## What is phpIPAM?
In short: an IPAM is one of the core pieces (or maybe even *the* core piece) of an IT management infrastructure. It is the building block upon which you can build automated IT management systems. (Monitoring, Changes, DNS, etc.) An IPAM keeps track of IP networks, VLANs, circuts, hosts, locations and how all of these are related. If you manage more than four networks/VLANS/locations, an IPAM is a good way to keep track of it all. There are other IPAMs than phpIPAM. I like phpIPAM.
See [here](https://github.com/phpipam/phpipam)


## What is ansible?
Ansible is a framework for building an automated IT management system. It has a bit of a learning curve. It may appear clunky at first. Like learning how to play the guitar. If you no longer reliably can count the number of hosts you manage from the top of your head, you may have reason to look into ansible. 
See [here](https://github.com/ansible/ansible).


## Who wrote this?
Someone whose day job is not writing python or SQL. I rely heavily on w3schools, stackoverflow and big G. You have been warned.

