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
from annoying.decorators import render_to
from simplepagination import paginate
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from uglyrate.forms import RateForm
from serializator.utils import ajax_request


@permission_required('add_rate')
@ajax_request
def create(request):
    """Create new rate"""
    if request.method == 'POST':
        form = RateForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return {
                'error': None,
                'user': form.cleaned_data['enemy'].values(
                    'id', 'rate_count', 'username',
                )
            }


@ajax_request
def get_top(request, offset=0, count=100):
    """Get ugliest users"""
    if offset < 0:
        offset = 0
    count = 100 if 500 < count <= 0 else count
    return User.objects.order_by('-rate_count').values(
        'id', 'rate_count', 'username'
    )[offset:][:count]


@render_to('uglyrate/top.html')
@paginate(style='digg', per_page=50)
def top(request):
    """Get top uglys"""
    return {
        'object_list': User.objects.filter(ignored=False).order_by('-rate_count')
    }
