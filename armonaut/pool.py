import typing


class WorkerPool(object):
    """Base class for a worker pool that is created from a WorkerPoolManager class."""
    def __init__(self, id: str, host: str):
        self.id = id
        self.host = host

    def container_units(self) -> typing.Tuple[int, int, int]:
        """Returns the number of container units that are available, in-use,
        and total for the pool.
        
        :returns: A tuple containing available, in-use and total container units.
        """
        raise NotImplementedError()

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id} host={self.host}>'

    def __str__(self):
        return self.__repr__()


class WorkerPoolManager(object):
    """Base class for a worker pool manager that can manage a group of worker
    pools from a cloud-computing provider such as Scaleway or Amazon EC2.
    The manager is used to calculate theoretical through-put of a set of
    worker pools and are used to figure out which worker pools can be allocated
    or deallocated in order to accomodate for a growing queue or to save money.
    """
    def __init__(self, id: str, pool_size: int, max_pools):
        self.id = id
        self.pool_size = pool_size
        self.pools = []
        self.max_pools = max_pools

    def container_units(self) -> typing.Tuple[int, int, int]:
        available = 0
        in_use = 0
        total = 0

        for pool in self.pools:
            a, i, t = pool.container_units()
            available += a
            in_use += i
            total += t

        return available, in_use, total

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


class C2MPoolManager(WorkerPoolManager):
    def __init__(self):
        super(C2MPoolManager, self).__init__('C2M', 8, 5)


class C2SPoolManager(WorkerPoolManager):
    def __init__(self):
        super(C2SPoolManager, self).__init__('C2S', 4, 10)


class VC1LPoolManager(WorkerPoolManager):
    def __init__(self):
        super(VC1LPoolManager, self).__init__('VC1L', 3, 10)


class VC1MPoolManager(WorkerPoolManager):
    def __init__(self):
        super(VC1MPoolManager, self).__init__('VC1M', 2, 25)
