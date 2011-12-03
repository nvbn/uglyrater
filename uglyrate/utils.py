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
import re
from django.utils.translation import ugettext as _
import httplib

NONE_USER = 0
VK_USER = 1
FB_USER = 2


class RatingDisabled(Exception):
    """User disable rating exception"""

    def __init__(self, user):
        super(RatingDisabled, self).__init__(
            _(u'%(user)s disable ratings!') % {
                'user': user,
            }
        )


class RateAlreadyExist(Exception):
    """User already rated exception"""

    def __init__(self, user):
        super(RateAlreadyExist, self).__init__(
            _(u'You already rate %(user)s') % {
                'user': user,
            }
        )


def check_url(addr, name):
    """Check url exist"""
    conn = httplib.HTTPConnection(addr)
    conn.request('GET', '/' + name)
    response = conn.getresponse()
    return response.status == 200


def get_name_from_url(url):
    """Get fb or vk name from url"""
    vk = re.search(r'(.*)[vk\.com,vkontakte\.ru]/([^/]*)(/*)', url)
    if vk:
        vk_name = vk.group(2)
        if vk_name and check_url('vk.com', vk_name):
            return VK_USER, vk_name
    fb = re.search(r'(.*)facebook.com/(.*id=)*([^/?]*)(/*)', url)
    if fb:
        fb_name = fb.group(3)
        if fb_name and check_url('facebook.com', fb_name):
            return FB_USER, fb.group(3)
    return NONE_USER, None
