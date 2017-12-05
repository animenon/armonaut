# Copyright (C) 2017 Seth Michael Larson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import redis
from rq import Worker, Queue, Connection


conn = redis.StrictRedis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))


if __name__ == '__main__':  # pragma: no coverage
    with Connection(conn):
        worker = Worker(map(Queue, ['high', 'default', 'low']))
        worker.work()
