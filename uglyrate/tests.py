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

from django.contrib.auth.models import User
from uglyrate.models import Rate
from uglyrate.utils import RateAlreadyExist, RatingDisabled
from uglyrate.forms import RateForm
import unittest


class RateTestCase(unittest.TestCase):
    """Test rates"""

    def setUp(self):
        """Create test users"""
        self.users = map(lambda number: User.objects.create(
            username=str(number),
        ), range(100))

    def checkCreating(self):
        """Check users creating"""
        for num, user in enumerate(self.users[20:]):
            self.assertIsNotNone(Rate.objects.create(
                user=user,
                enemy=self.users[num + 5],
            ), 'Creating not work!')
        for num, user in enumerate(self.users[20:]):
            self.assertRaises(RateAlreadyExist,
                Rate.objects.create(
                    user=user,
                    enemy=self.users[num + 5],
                ),
            'Dublicates!')
        for num, user in enumerate(self.users[:20]):
            user.ignored = True
            user.save()
            self.assertRaises(RatingDisabled,
                Rate.objects.create(
                    user=self.users[num - 1],
                    enemy=user,
                ),
            'Ignoring not work!')

    def checkCreatingWithFrom(self):
        """Check creating with form"""
        for num, user in enumerate(self.users[20:]):
            form = RateForm(user, {'enemy': 'http:/facebook.com/profile.php?id=%d' % self.users[num + 5]})
            self.assertIsNotNone(
                form.is_valid(),
                'Creating with form not work!'
            )
        for num, user in enumerate(self.users[20:]):
            form = RateForm(user, {'enemy': self.users[num + 5]})
            self.assertIs(
                form.is_valid(),
                False,
                'Form validating not work!'
            )
            self.assertIsNotNone(
                form.errors,
                'Form validating with errors!'
            )
        for num, user in enumerate(self.users[:20]):
            user.ignored = True
            user.save()
            form = RateForm(user, {
                'enemy': self.users[num - 1]
            })
            self.assertIs(
                form.is_valid(),
                False,
                'Form validating not work with ignoring!'
            )
            self.assertIsNotNone(
                form.errors,
                'Form validating with errors with ignoring!'
            )
