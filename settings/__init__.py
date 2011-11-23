#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

try:
    from base import *
except ImportError, e:
    import traceback, sys
    sys.stderr.write('Unable to read settings/base.py\n')
    sys.stderr.write(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
    sys.stderr.write("%s\n" %e)
    sys.exit(1)

try:
    from local import *
except ImportError, e:
    import sys
    sys.stderr.write('Unable to read settings/local.py\nTry copy settings/dist.py to settings/local.py\n')
    sys.stderr.write("%s\n" %e)
    sys.exit(1)