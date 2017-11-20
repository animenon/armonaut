class WorkerPool(object):
    """Base class for a worker pool that is created from a WorkerPoolManager class."""
    def __init__(self, id: str, host: str):
        self.id = id
        self.host = host

    @property
    def available_container_units(self) -> int:
        raise NotImplementedError()


class WorkerPoolManager(object):
    """Base class for a worker pool manager that can manage a group of worker
    pools from a cloud-computing provider such as Scaleway or Amazon EC2.
    The manager is used to calculate theoretical through-put of a set of
    worker pools and are used to figure out which worker pools can be allocated
    or deallocated in order to accomodate for a growing queue or to save money.
    """
    def __init__(self, id: str, pool_size: int):
        self.id = id
        self.pool_size = pool_size
        self.pools = []
        
    @property
    def maximum_container_units(self) -> int:
        return len(self.pools) * self.pool_size
        
    @property
    def available_container_units(self) -> int:
        return sum([p.available_container_units for p in self.pools])

    def allocate_pool(self) -> WorkerPool:
        raise NotImplementedError()
        
    def deallocate_pool(self, pool_id: str):
        raise NotImplementedError()
        
    def refresh_pools(self):
        raise NotImplementedError()
        
    def __repr__(self):
        return f'<{type(self).__name__} id=\'{self.id}\' workers={self.pools * self.pool_size}>'
        
    def __str__(self):
        return self.__repr__()


class ScalewayC2mPoolManager(WorkerPoolManager):
    def __init__(self):
        super(ScalewayC2MPoolManager, self).__init__('scaleway-c2m', 8)


class ScalewayC2sPoolManager(WorkerPoolManager):
    def __init__(self):
        super(ScalewayC2SPoolManager, self).__init__('scaleway-c2s', 4)
        
        
class Ec2C4xlargePoolManager(WorkerPoolManager):
    def __init__(self):
        super(Ec2C4xlargePoolManager, self).__init__('ec2-c4.xlarge', 4)
