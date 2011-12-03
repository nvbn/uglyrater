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
from uglyrate.utils import RatingDisabled, RateAlreadyExist,\
    get_name_from_url, NONE_USER, VK_USER, FB_USER


class RateForm(forms.ModelForm):
    """Form for creating rates"""
    enemy = forms.CharField(label=_('user page'))

    def __init__(self, user, *args, **kwargs):
        """Init form and set user"""
        self.user = user
        super(RateForm, self).__init__(*args, **kwargs)

    def clean_enemy(self):
        """Call hash generator"""
        data = self.cleaned_data['enemy']
        _type, name = get_name_from_url(data)
        print _type, name
        if _type is NONE_USER:
            raise forms.ValidationError(_('This profile does not exist!'))
        elif _type is VK_USER:
            user = User.objects.get_or_create(
                vk_id=name,
            )
        elif _type is FB_USER:
            user = User.objects.get_or_create(
                fb_id=name,
            )
        try:
            self.instance.hash = Rate.gen_hash(self.user, user)
        except RatingDisabled:
            raise forms.ValidationError(_('This user disable ratings!'))
        except RateAlreadyExist:
            raise forms.ValidationError(_('You already rate this user!'))
        return user

    def save(self, commit=True):
        result = super(RateForm, self).save(commit)
        user = self.cleaned_data.get('enemt')
        user.rate_count += 1
        user.save()
        return result

    class Meta:
        model = Rate
        fields = []
