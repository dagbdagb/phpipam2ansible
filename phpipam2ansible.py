#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
#

#  phpipam2ansible.py
#  
#  Copyright 2019 Dag Bakke <igotemail@thisisadummy.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# dag - at - bakke - dot - com

import sys
import argparse
import pymysql as mdb
import json


dbcreds = '~/.my.cnf'
groups = {}

# These queries should return a two-column wide table, with whatever value you want in the first column, and the hostname in the other.
# If it isn't clear, the first column becomes the group name the host should belong to, and the column must be named 'AS groupname'..
#
# Each host can perfectly well be a member of multiple groups. It is kind of the idea.
# This way you can logically AND/OR/NOT groups (and hosts/IPs) in ansible to really narrow it down.
# See: https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html#common-patterns
#
# phpIPAM permits custom fields for many things, and we use this extensively. You could too.

queries = [ "SELECT tname AS groupname, hostname FROM deviceTypes,devices WHERE tid=type ORDER BY tname,hostname",
#        "SELECT custom_field AS groupname, hostname FROM devices,locations WHERE custom_field IS NOT NULL AND devices.location = locations.id ORDER BY custom_field,hostname",
#        "SELECT substring(custom_field,1,4) AS groupname, hostname FROM devices WHERE custom_field IS NOT NULL ORDER BY custom_field,hostname",
#        "SELECT 'inactive' AS groupname, hostname FROM devices,locations WHERE devices.location = locations.id AND (now() BETWEEN custom_inactive_date AND custom_active_date)",
    ]


def getdbdata(query):
    mylist = []
    if DEBUG:
        print(query)

    try:
        con = mdb.connect(read_default_file=dbcreds, read_default_group='phpipamro')
        cursor = con.cursor()
        cursor.execute(query)
        desc = cursor.description
        column_names = [col[0] for col in desc]

        rows = cursor.fetchall()
        for row in rows:
            mylist.append(dict(zip(column_names, row)))

    except Exception as ex:
        print(ex)
        print("Check db communication.")

    finally:
        if con:
            con.close()

    return mylist


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true', default=False, help="show debug output")
    parser.add_argument('--list', action='store_true', help="used by ansible")
    parser.add_argument('--groups', action='store_true', help="list groupnames this script generates")
    parser.add_argument('--host', action='store', help="unused") 
    myargs = parser.parse_args()

    global DEBUG
    DEBUG = myargs.debug

    # Create the groups dict which we will populate
    groups = {}
    groups['_meta'] = {}
    groups['_meta']['hostvars'] = {}

    # loop through the queries and populate the groups dict with data found
    for query in queries:
        result = getdbdata(query.format( ** vars(myargs) ))
        for item in result:
            if DEBUG:
                print(item)
            if not (groups.get(item['groupname'], None)): # Check if groupname is known
                groups[item['groupname']] = {}            # If not, add it
                groups[item['groupname']]['hosts'] = []   # ...and the hosts list
                groups[item['groupname']]['vars'] = {}    # ...and the vars dict

            groups[item['groupname']]['hosts'].append(item['hostname']) 
            groups['_meta']['hostvars'][item['hostname']] = {}

    if myargs.list:
        print(json.dumps(groups))

    if myargs.groups:
        for key in groups.keys():
            print(key)

    # We return '_meta', skipped implementing --host option.

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
