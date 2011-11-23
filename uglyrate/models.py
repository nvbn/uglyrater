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
from django.utils.translation import ugettext_lazy as _
import hashlib

class RateManager(models.Manager):
    
    def create(self, **kwargs):
        if 'user' in kwargs and 'enemy' in kwargs:
            kwargs['hash'] = hashlib.md5('%d%d' % (kwargs['user'].id, kwargs['enemy'].id))
        super(RateManager, self).create(**kwargs)
        
        
class Rate(models.Model):
    hash = models.CharField(max_length=32, verbose_name=_('hash'), unique=True)
    objects = RateManager()