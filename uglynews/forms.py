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

from django import forms
from uglynews.models import News
from djang0parser.utils import parse


class CreateNewsForm(forms.ModelForm):
    """News creating form"""
    def __init__(self, user, *args, **kwargs):
        """Specif author"""
        self.user = user
        super(CreateNewsForm, self).__init__(*args, **kwargs)

    def clean_text(self):
        """Sanitize text"""
        return parse(self.cleaned_data.get('text'))

    def clean(self):
        """Clean and add author"""
        self.instance.author = self.user
        return self.cleaned_data

    class Meta:
        model = News
        fields = ('title', 'text', 'tags')
