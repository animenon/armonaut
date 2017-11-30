import os
import paramiko
import typing
import requests
import uuid


SCALEWAY_REGIONS = ['par1', 'ams1']
SCALEWAY_SERVER_TYPES = ['C2M', 'C2S', 'VC1L', 'VC1M', 'VC1S']


class WorkerPool(object):
    """Base class for a worker pool that is created from a WorkerPoolManager class."""
    def __init__(self, region: str, server_type: str, id: str):
        self.region = region
        self.server_type = server_type
        self.id = id

    def power_on(self):
        return self._action('poweron')

    def power_off(self):
        return self._action('poweroff')

    def restart(self):
        return self._action('restart')

    def _action(self, action):
        with requests.post(f'https://cp-{self.region}.scaleway.com/servers/{self.id}/action',
                           json={'action': action}) as r:
            if r.status_code == 202:
                return True
        return False

    def __repr__(self):
        return f'<{type(self).__name__} region={self.region} server_type={self.server_type} id={self.id}>'

    def __str__(self):
        return self.__repr__()


class WorkerPoolManager(object):
    """Base class for a worker pool manager that can manage a group of worker
    pools from a cloud-computing provider such as Scaleway or Amazon EC2.
    The manager is used to calculate theoretical through-put of a set of
    worker pools and are used to figure out which worker pools can be allocated
    or deallocated in order to accomodate for a growing queue or to save money.
    """
    def __init__(self, id: str):
        self.id = id
        self.pools = []

    def allocate_pool(self):
        for server_type in SCALEWAY_SERVER_TYPES:
            for region in SCALEWAY_REGIONS:
                try:
                    with requests.post(f'https://cp-{region}.scaleway.com/servers',
                                       headers={'X-Auth-Token': os.environ['SCALEWAY_API_SECRET']},
                                       json={'organization': os.environ['SCALEWAY_ORGANIZATION_ID'],
                                             'name': uuid.uuid4().hex,
                                             'image': 'c1d407de-0d4c-462c-95df-42a2fe0479fe',  # Debian Stretch (9)
                                             'commercial_type': server_type,
                                             'enable_ipv6': True,
                                             'tags': ['armonaut']}) as r:

                        # Our pool started running,
                        if r.status_code == 201:
                            server = r.json()


                except Exception:
                    pass


    def deallocate_pool(self):
        self.refresh_pools()
        for pool in sorted(self.pools, key=lambda p: (SCALEWAY_SERVER_TYPES.index(p.server_type))):
            with requests.delete(f'https://cp-{pool.region}.scaleway.com/servers/{pool.id}',
                                 headers={'X-Auth-Token': os.environ['SCALEWAY_API_TOKEN']}) as r:
                if r.status_code == 204:
                    break

    def refresh_pools(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'<{type(self).__name__} id=\'{self.id}\'>'

    def __str__(self):
        return self.__repr__()
