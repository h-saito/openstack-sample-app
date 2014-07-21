#!/usr/bin/env python
#coding: utf-8 -*-

try:
    from novaclient import client as nova_client
    from novaclient import exceptions
    import time
except ImportError:
    print("failed=True msg='novaclient is required for this module'")

DOCUMENTATION = '''
---
module: hp_nova_floating_ip
version_added: "1.6.6"
short_description: Create/Delete floating_ip from OpenStack
description:
   - Create or Remove floating_ip from OpenStack.
options:
   login_username:
     description:
        - login username to authenticate to keystone
     required: true
     default: admin
   login_password:
     description:
        - Password of login user
     required: true
     default: 'yes'
   login_tenant_name:
     description:
        - The tenant name of the login user
     required: true
     default: 'yes'
   auth_url:
     description:
        - The keystone url for authentication
     required: false
     default: 'http://127.0.0.1:35357/v2.0/'
   api_version:
     description:
        - The version number or nova api
     required: true
     default: '2'
   name:
     description:
        - associate floating_ip to server name
     required: true
     default: None
   fixed_ip:
     description:
        - associate floating_ip to fixed_ip on server
     required: false
     default: None
   floating_ip:
     description:
        - delete floating ip from OpenStack
     required: false
     default: None
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     default: present
requirements: ["novaclient"]
'''

EXAMPLES = '''
# Associate floating_ip to server
- nova_compute:
       state: present
       login_username: admin
       login_password: admin
       login_tenant_name: admin
       name: app_server
       fixed_ip: 10.0.0.10
       floating_ip: 172.16.100.10
'''

def _remove_floating_ip(module, nova):
    try:
        server = nova.servers.find(name=module.params['name'])
        server.remove_floating_ip(module.params['floating_ip'])
    except Exception, e:
            module.fail_json( msg = "Error in remove floating_ip from server: %s " % e.message)
    module.exit_json(changed = True,
                     id=server.id,
                     name=server.name,
                     floating_ip=module.params['floating_ip'])

def _add_floating_ip(module, nova):
    try:
        server = nova.servers.find(name=module.params['name'])
        server.add_floating_ip(module.params['floating_ip'], fixed_address=module.params['fixed_ip'])
    except Exception, e:
        module.fail_json( msg = "Error in add floating_ip to server: %s" % e.message)
    module.exit_json(changed = True,
                     id=server.id,
                     name=server.name,
                     fixed_ip=module.params['fixed_ip'],
                     floating_ip=module.params['floating_ip'])


def main():
    module = AnsibleModule(
        argument_spec                   = dict(
        login_username                  = dict(default='admin'),
        login_password                  = dict(required=True),
        login_tenant_name               = dict(required=True),
        auth_url                        = dict(default='http://127.0.0.1:35357/v2.0/'),
        api_version                     = dict(default='2'),
        name                            = dict(required=True),
        fixed_ip                        = dict(default=None),
        floating_ip                     = dict(required=True),
        state                           = dict(default='present', choices=['absent', 'present']),
        ),
    )

    nova = nova_client.Client(module.params['api_version'],
                              module.params['login_username'],
                              module.params['login_password'],
                              module.params['login_tenant_name'],
                              module.params['auth_url'])
    try:
        nova.authenticate()
    except exceptions.Unauthorized, e:
        module.fail_json(msg = "Invalid OpenStack Nova credentials.: %s" % e.message)
    except exceptions.AuthorizationFailure, e:
        module.fail_json(msg = "Unable to authorize user: %s" % e.message)

    if module.params['state'] == 'present':
        _add_floating_ip(module, nova)
    if module.params['state'] == 'absent':
        _remove_floating_ip(module, nova)

# this is magic, see lib/ansible/module.params['common.py
from ansible.module_utils.basic import *
main()

# [EOF]
