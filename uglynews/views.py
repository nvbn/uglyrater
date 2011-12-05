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
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from simplepagination import paginate
from uglynews.models import News
from uglynews.forms import CreateNewsForm, EditNewsForm


@render_to('uglynews/news.html')
@paginate(style='digg', per_page=10)
def news(request):
    """Display news list"""
    return {
        'object_list': News.objects.filter(
            display=True
        ).select_related('author').order_by('-id')
    }


@render_to('uglynews/single_news.html')
def single_news(request, post_id):
    """Display single news"""
    post = get_object_or_404(News, id=post_id)
    return {
        'post': post,
    }


@render_to('uglynews/create_news.html')
@permission_required('add_news')
def create_news(request):
    """Create new post"""
    if request.method == 'POST':
        form = CreateNewsForm(request.user, request.POST)
        if form.is_valid():
            post = form.save()
            return redirect(reverse('uglynews_single_news', kwargs={
                'id': post.id,
            }))
    else:
        form = CreateNewsForm
    return {
        'form': form,
    }


@login_required
@render_to('uglynews/edit_news.html')
def edit_news(request, id):
    """Edit news post"""
    news = get_object_or_404(News, id=id)
    if not (
        request.user.has_perm('change_news') or
        request.user == news.author
    ):
        raise Exception("You can't do it!")
    if request.method == 'POST':
        form = EditNewsForm(news, request.POST)
        if form.is_valid():
            post = form.save()
            return redirect(reverse('uglynews_single_news', kwargs={
                'id': post.id,
            }))
    else:
        form = EditNewsForm(news)
    return {
        'form': form,
    }
