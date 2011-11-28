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
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from uglyrate.models import Rate
from uglyrate.utils import RatingDisabled, RateAlreadyExist


class RateForm(forms.ModelForm):
    """Form for creating rates"""
    enemy = forms.ModelChoiceField(User, required=True, label=_('user'))

    def __init__(self, user, *args, **kwargs):
        """Init form and set user"""
        self.user = user
        super(RateForm, self).__init__(*args, **kwargs)

    def clean_enemy(self):
        """Call hash generator"""
        data = self.cleaned_data['enemy']
        try:
            self.instance.hash = Rate.gen_hash(self.user, data)
        except RatingDisabled:
            raise forms.ValidationError(_('This user disable ratings!'))
        except RateAlreadyExist:
            raise forms.ValidationError(_('You already rate this user!'))
        return data

    def save(self, commit=True):
        result = super(RateForm, self).save(commit)
        self.user.rate_count += 1
        self.user.save()
        return result

    class Meta:
        model = Rate
        fields = []
