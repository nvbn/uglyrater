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
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from serializator.utils import ajax_request
from uglycomments.forms import CommentForm
from uglycomments.models import Comment


@permission_required('add_comment')
@ajax_request
def reply(request, root_id):
    """Reply to obj or comment"""
    root = get_object_or_404(Comment, id=root_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = root.reply({
                'text': form.cleaned_data['text'],
                'author': request.user,
            })
            return {
                'status': True,
                'comment': comment
            }
        else:
            return {
                'status': False,
                'errors': form.errors,
            }
    return {
        'status': False
    }
  