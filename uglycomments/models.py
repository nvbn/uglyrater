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

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from treebeard.mp_tree import MP_Node
from django.utils.translation import ugettext as _
from serializator.utils import Serializable
from uglycomments.subclass import receiver_subclasses


class Comment(MP_Node, Serializable):
    """Comment node"""
    serialize_fields = ['id', 'author', 'text', 'depth', 'path']
    author = models.ForeignKey(User, verbose_name=_('author'))
    text = models.TextField(verbose_name=_('text'))
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def reply(self, **kwargs):
        """Reply to comment"""
        kwargs['content_object'] = self.content_object
        return self.add_child(**kwargs)


class ModelWithComments(models.Model):
    """Abstract model with comments class"""
    root = models.ForeignKey(Comment, verbose_name=_('comment root'))

    def comments(self):
        """Get all comments"""
        return self.root.get_tree()

    def reply(self, comment_id=None, **kwargs):
        """Reply to comment

        Keywords Arguments:
        comment_id -- int

        Returns: Comment
        """
        if comment_id:
            root = Comment.objects.get(id=comment_id)
        else:
            root = self.root
        return root.reply(**kwargs)

    class Meta:
        abstract = True


@receiver_subclasses(post_save, ModelWithComments, 'with_comments_post_save')
def create_root(sender, instance, **kwargs):
    """Create comment root"""
    if not instance.root:
        instance.root = Comment.add_root(
            content_object=instance,
        )