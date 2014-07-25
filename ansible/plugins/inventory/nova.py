#!/usr/bin/env python

import os
import sys
from novaclient import client as nova_client
try:
    import json
except:
    import simplejson as json


OS_USERNAME = os.environ.get('OS_USERNAME')
OS_PASSWORD = os.environ.get('OS_PASSWORD')
OS_TENANT_NAME = os.environ.get('OS_TENANT_NAME')
OS_AUTH_URL = os.environ.get('OS_AUTH_URL')
OS_REGION_NAME = os.environ.get('OS_REGION_NAME')
NOVA_API_VERSION = '2'
EXCLUDE_HOST = ['step-server']


def get_host(host):
    # Get Host Information
    return get_list()[OS_TENANT_NAME]['_meta']['hostvars'][host]


def get_list():
    # Generate Inventory File
    inventory = {}
    hosts = []
    inventory[OS_TENANT_NAME] = dict(hosts=dict(),
                                     vars=dict(),
                                     _meta=dict(hostvars=dict()))
    hostvars = inventory[OS_TENANT_NAME]['_meta']['hostvars']

    nova = nova_client.Client(NOVA_API_VERSION,
                              OS_USERNAME,
                              OS_PASSWORD,
                              OS_TENANT_NAME,
                              OS_AUTH_URL,
                              region_name=OS_REGION_NAME)
    servers = nova.servers.list()
    networks = {}
    for s in servers:
        if s.name in EXCLUDE_HOST:
            continue
        floating_ips = [i['addr'] for i in s.addresses.itervalues().next() if i['OS-EXT-IPS:type'] == 'floating']
        hostvars[floating_ips[0]] = dict(name=s.name, id=s.id,
                                         flavor=s.flavor['id'], image=s.image['id'],
                                         key_name=s.key_name,
                                         security_groups=[sg['name'] for sg in s.security_groups],
                                         networks=s.addresses,
                                         status=s.status)
        hosts.append(floating_ips[0])
    inventory[OS_TENANT_NAME]['hosts'] = hosts

    return inventory


# main
if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
    inventory = get_list()
elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
    inventory = get_host(sys.argv[2])
else:
    print("Usage: %s --list or --host <hostname>" % sys.argv[0])
    sys.exit(1)
print(json.dumps(inventory, sort_keys=True, indent=2))

# [EOF]