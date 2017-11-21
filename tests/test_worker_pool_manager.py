import mock
from armonaut.pool import WorkerPoolManager


def test_container_units():
    m1 = mock.Mock()
    m1.container_units.return_value = (1, 2, 3)
    m2 = mock.Mock()
    m2.container_units.return_value = (0, 3, 7)

    pm = WorkerPoolManager('test', 4)
    pm.pools.append(m1)
    pm.pools.append(m2)

    assert pm.container_units() == (1, 5, 10)
