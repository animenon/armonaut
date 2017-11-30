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

"""Small script which sets up Heroku environment variables for a given application 
in the local terminal. Works for both Windows and Linux. Run the file that is
generated after running heroku config.
"""

import os
import re
import sys
import platform
import subprocess


def main():
    if len(sys.argv) == 1:
        app = 'armonaut'
    else:
        app = sys.argv[1]

    if platform.system() == 'Windows':
        filename = 'setup-env.bat'
        export = 'set'
    else:
        filename = 'setup-env.sh'
        export = 'export'

    path = os.path.relpath(os.path.join(os.path.dirname(__file__), filename), os.getcwd())
    output = subprocess.check_output('heroku config --app %s' % app, shell=True)
    output = output.decode('utf-8')

    with open(path, 'w+') as f:
        f.truncate()
        for name, value in re.findall('^([A-Z0-9_]+):\s+([^\s].*)$', output, re.MULTILINE):
            f.write('%s %s=%s\n' % (export, name, value))

    if platform.system() == 'Windows':
        print('Execute `.\\%s` to activate environment.' % path)
    else:
        print('Execute `source %s` to activate environment.' % path)


if __name__ == '__main__':
    main()
