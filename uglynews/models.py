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
from tagging.fields import TagField
from datetime import datetime
from serializator.utils import Serializable


class News(models.Model, Serializable):
    """Simple new object"""
    serialize_fields = ['author', 'title', 'id']
    author = models.ForeignKey(User, verbose_name=_('author'))
    title = models.CharField(max_length=512, verbose_name=_('title'))
    preview = models.TextField(verbose_name=_('preview'))
    text = models.TextField(verbose_name=_('text'))
    tags = TagField(blank=True, null=True, verbose_name=_('tags'))
    created = models.DateTimeField(default=datetime.now(), verbose_name=_('created'))
    display = models.BooleanField(default=True, verbose_name=_('display'))
