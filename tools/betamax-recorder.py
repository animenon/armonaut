#!/usr/bin/env python
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

"""
This is the tool to use to create Betamax cassettes from recorded API calls
that are used within our unit tests for reliable and reproducible HTTP
interactions with other servers.

For more information visit the documentation: http://betamax.readthedocs.io
"""

import os
import betamax
import requests
import base64

# The cassette library is in `tests/cassettes`
CASSETTE_LIBRARY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'tests', 'cassettes'
)

def main():
    try:
        os.makedirs(CASSETTE_LIBRARY_DIR)
    except OSError:
        pass
    session = requests.Session()
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    recorder = betamax.Betamax(
        session,
        cassette_library_dir=CASSETTE_LIBRARY_DIR,
        default_cassette_options={
            'record_mode': 'once',
            'match_requests_on': ['method', 'uri', 'json-body'],
            'preserve_exact_body_bytes': True
        },
    )  # TODO: Add cassette placeholders for GitHub, GitLab, and BitBucket API tokens.

    # Modify requests here to record into the cassette.
    with recorder.use_cassette('example_request'):
        session.get('https://httpbin.org/get')


if __name__ == '__main__':
    main()
