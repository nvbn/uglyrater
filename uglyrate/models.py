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

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from uglyrate.utils import RatingDisabled, RateAlreadyExist
from serializator.utils import Serializable
import hashlib

User.add_to_class('rate_count', models.PositiveIntegerField(default=0, verbose_name=_('rate count')))
User.add_to_class('ignored', models.BooleanField(default=False, verbose_name=_('rate ignore')))
User.to_json = Serializable.to_json
User.set_fields = Serializable.set_fields
User.json_fields = ['id', 'username']

class RateManager(models.Manager):
    """Manager for Rate model"""

    def create(self, **kwargs):
        """Manager create method with hash generator"""
        if 'user' in kwargs and 'enemy' in kwargs:
            kwargs['hash'] = Rate.gen_hash(kwargs['user'], kwargs['enemy'])
            hash_generated = True
        else:
            hash_generated = False
        result = super(RateManager, self).create(**kwargs)
        if hash_generated:
            kwargs['user'].rate_count += 1
            kwargs['user'].save()
        return result
        
        
class Rate(models.Model):
    """Rates model"""
    hash = models.CharField(max_length=32, verbose_name=_('hash'), unique=True)
    objects = RateManager()

    @staticmethod
    def gen_hash(user, enemy):
        """Generate hash for anonymous rates

        Keywords Arguments:
        user -- User
        enemy -- User

        Returns: str
        """
        if enemy.ignored:
            raise RatingDisabled(enemy)
        if Rate.objects.filter(user=user, enemy=enemy).count():
            raise RateAlreadyExist(enemy)
        return hashlib.md5('%d%d' % (user.id, enemy.id)).hexdigest()