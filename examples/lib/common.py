#-*- coding: utf-8 -*-

__author__ = 'saito@fgrep.org'


import os
import sys


OS_USERNAME = os.environ.get('OS_USERNAME')
OS_PASSWORD = os.environ.get('OS_PASSWORD')
OS_TENANT_NAME = os.environ.get('OS_TENANT_NAME')
OS_AUTH_URL = os.environ.get('OS_AUTH_URL')
OS_REGION_NAME = os.environ.get('OS_REGION_NAME')

NOVA_API_VERSION = '2'
GLANCE_API_VERSION = '1'
CINDER_API_VERSION = '1'
## NEUTRON_API_VERSION = '2.0'


class OpenStackClient(object):
    def get(self):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def create(self, size, name):
        raise NotImplementedError

    def delete(self, id):
        raise NotImplementedError


class KeystoneClient(object):
    def __init__(self):
        from keystoneclient.v2_0.client import Client
        self.client = Client(username=OS_USERNAME, password=OS_PASSWORD,
                                tenant_name=OS_TENANT_NAME, auth_url=OS_AUTH_URL)

    def get_public_endpoints(self, endpoint_type='publicURL'):
        result = dict()
        service_types = ['compute', 'image', 'volume', 'network', 'identity']

        for service_type in service_types:
            result[service_type] = self.client.service_catalog.url_for(service_type=service_type,
                                                                            endpoint_type=endpoint_type)
        return result

    def get_public_endpoint(self, service_type, endpoint_type='publicURL'):
        return  self.client.service_catalog.url_for(service_type=service_type,
                                                    endpoint_type=endpoint_type)


class NovaClient(OpenStackClient):
    def __init__(self):
        from novaclient.client import Client
        self.client = Client(NOVA_API_VERSION, OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL)

    def list(self):
        """
        :rtype: dict of instances
        """
        instances = {}
        for server in self.client.servers.list():
            instances[server.id] = server.name
        return instances

    def list_flavors(self):
        """
        :rtype: dict of flavors
        """
        flavors = {}
        for flavor in self.client.flavors.list():
            flavors[flavor.id] = flavor.name
        return flavors

    def list_keypairs(self):
        """
        :rtype: dict of keypairs
        """
        keypairs = {}
        for keypair in self.client.keypairs.list():
            keypairs[keypair.id] = keypair.name
        return keypairs

    def list_security_groups(self):
        """
        :rtype: dict of security groups
        """
        secgroups = {}
        for secgroup in self.client.security_groups.list():
            secgroups[secgroup.id] = secgroup.name
        return secgroups

    def list_floating_ips(self, free=False):
        """
        :param free: if it is True, get unassigned address in floating_ips list
        :rtype: dict of floating addresses
        """
        ips = {}
        for ip in self.client.floating_ips.list():
            if free is True:
                if ip.instance_id is not None:
                    continue
            ips[ip.id] = ip.ip
        return ips

    def create(self, name, image, flavor, key_name, security_groups, nics):
        """
        :param name: display name of VM instance
        :param image: id of GuestOS image
        :param flavor: id of flavor
        :param key_name: name of public keypair
        :param security_groups: list of security groups
        :param nics: dict of network info in list is formatted  to "[{ 'net-id': 'uuid of network' },... ]"
        :rtype: :class: Server
        """
        return self.client.servers.create(name=name, image=image, flavor=flavor,
                                          key_name=key_name, security_groups=security_groups, nics=nics)

    def delete(self, id):
        """
        :param id: id of instance
        """
        server= self.client.servers.get(id)
        self.client.servers.delete(server)

    def create_floating_ip(self):
        """
        :rtype: :class: FloatingIP
        """
        return self.client.floating_ips.create()

    def delete_floating_ip(self):
        """
        :param id: id of floating_ip
        """
        server= self.client.servers.get(id)
        self.client.floating_ips.delete(id)

    def add_floating_ip(self, server, address):
        """
        :param server: id of instance
        :param address: IPAddress of unassigned floating_ip
        """
        self.client.servers.add_floating_ip(server, address)

    def remove_floating_ip(self, server, address):
        """
        :param server: id of instance
        :param address: IPAddress of assigned floating_ip on target instance
        """
        self.client.servers.remove_floating_ip(server, address)

    def attach_volume(self, server_id, volume_id, device):
        """
        :param server_id: id of instance
        :param volume_id: id of volume for attach to instance
        :param device: device path on instance
        :rtype: :class: Volume
        """
        return self.client.volumes.create_server_volume(server_id=server_id, volume_id=volume_id, device=device)

    def detach_volume(self, server_id, attachment_id):
        """
        :param server_id: id of instance
        :param volume_id: id of volume for detach from instance
        """
        self.client.volumes.delete_server_volume(server_id=server_id, attachment_id=attachment_id)


class GlanceClient(OpenStackClient):
    def __init__(self):
        token = KeystoneClient().client.auth_token
        endpoint = KeystoneClient().get_public_endpoint('image')
        from glanceclient.client import Client
        self.client = Client(GLANCE_API_VERSION, token=token, endpoint=endpoint)

    def list(self):
        """
        :rtype: dict of images
        """
        images = {}
        for image in self.client.images.list():
            images[image.id] = image.name
        return images


class CinderClient(OpenStackClient):
    def __init__(self):
        from cinderclient.client import Client
        self.client = Client(CINDER_API_VERSION, OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL)

    def list(self, free=False):
        """
        :rtype: dict of volumes
        """
        volumes = {}
        for volume in self.client.volumes.list():
            if free is True:
                if len(volume.attachments) > 0:
                    continue
            volumes[volume.id] = volume.display_name
        return volumes

    def create(self, size, name):
        """
        :param size: size of volume
        :param name: display name of volume
        :rtype: :class: Volume
        """
        return self.client.volumes.create(size=size, display_name=name)

    def delete(self, id):
        """
        :param id: id of volume
        """
        volume = self.client.volumes.get(id)
        self.client.volumes.delete(volume)


class NeutronClient(OpenStackClient):
    def __init__(self):
        ## token = KeystoneClient().client.auth_token
        ## endpoint_url = KeystoneClient().get_public_endpoint('image')
        ## from neutronclient.neutron.client import Client
        ## self.client = Client(NEUTRON_API_VERSION, token=token, endpoint_url=endpoint_url)
        from neutronclient.v2_0.client import Client
        self.client = Client(username=OS_USERNAME, password=OS_PASSWORD,
                             tenant_name=OS_TENANT_NAME, auth_url=OS_AUTH_URL)
    def list(self):
        """
        :rtype: dict of networks
        """
        networks = {}
        for network in self.client.list_networks()['networks']:
            networks[network['id']] = network['name']
        return networks


##
## [EOF]
##