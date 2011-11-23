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

from functools import wraps
import json
from django.db.models import Model
from django.http import HttpResponse

class SpecialModelEncoder(json.JSONEncoder):
    """Special encoder"""

    def default(self, obj):
        """Prepare for json"""
        if isinstance(obj, Model) and hasattr(obj, 'to_json'):
            return obj.to_json()
        try:
            return map(lambda item: self.default(item), obj)
        except TypeError:
            try:
                return json.JSONEncoder.default(self, obj)
            except TypeError:
                return obj


class Serializable(object):
    """Serializable class"""

    def __init__(self):
        self.json_fields = []

    def to_json(self, *args):
        if not len(args):
            args = self.json_fields
        return dict(map(lambda arg: (
            arg, SpecialModelEncoder().default(reduce(
                lambda obj, attr: getattr(obj, attr),
                [self] + arg.split('__')
            ))
        ),args))

    def set_fields(self, *args):
        """Set fields for serialize"""
        self.json_fields = args
        return self


class JsonResponse(HttpResponse):#modified from annoying
    """
     HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=SpecialModelEncoder().encode(data), mimetype='application/json')


def ajax_request(func):
    """
    If view returned serializable dict, returns JsonResponse with this dict as content.

    example:

        @ajax_request
        def my_view(request):
            news = News.objects.all()
            news_titles = [entry.title for entry in news]
            return {'news_titles': news_titles}
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper