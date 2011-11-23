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
from serializator.utils import Serializable, SpecialModelEncoder
from django.utils.translation import ugettext as _
import unittest

class TestModel(models.Model, Serializable):
    """Fake test models"""
    testfield = models.IntegerField()

    def __init__(self, *args, **kwargs):
        """Initiale with json fields"""
        super(TestModel, self).__init__(*args, **kwargs)
        self.json_fields = ['id', 'testfield']


class TestModel2(models.Model, Serializable):
    """Test model with foreign key"""
    testfield = models.IntegerField()
    testfield1 = models.ForeignKey(TestModel)

    def __init__(self, *args, **kwargs):
        """Initiale with json fields"""
        super(TestModel2, self).__init__(*args, **kwargs)
        self.json_fields = ['id', 'testfield', 'testfield1']


class SerializatorTestCase(unittest.TestCase):
    """Serializator tests"""

    def setUp(self):
        """Create test objects"""
        self.testmodels = map(lambda number: TestModel.objects.create(
            testfield=number
        ), range(100))
        self.testmodels2 = map(lambda test1: TestModel2.objects.create(
            testfield=test1.testfield,
            testfield1=test1
        ), self.testmodels)

    def testOnce(self):
        """Test single object serialization"""
        for obj in self.testmodels:
            self.assertEqual(
                SpecialModelEncoder().default(obj),
                {
                    'testfield': obj.testfield,
                    'id': obj.id,
                },
                _('Serialization failed!')
            )
        for obj in self.testmodels2:
            self.assertEqual(
                SpecialModelEncoder().default(obj),
                {
                    'testfield': obj.testfield,
                    'testfield1': {
                        'testfield': obj.testfield1.testfield,
                        'id': obj.testfield1.id,
                    }, 'id': obj.id,
                },
                _('Serialization objects with foreign failed!')
            )

    def testQS(self):
        """Test qs and list serialization"""
        result = SpecialModelEncoder().default(self.testmodels)
        for obj in self.testmodels:
            self.assertIn({
                'testfield': obj.testfield,
                'id': obj.id,
            }, result, _('Serialize of list not work!'))
        result = SpecialModelEncoder().default(self.testmodels2)
        for obj in self.testmodels2:
            self.assertIn({
                'testfield': obj.testfield,
                'testfield1': {
                    'testfield': obj.testfield1.testfield,
                    'id': obj.testfield1.id
                }, 'id': obj.id,
            }, result, _('Serialize of list with foreign key not work!'))
        result = SpecialModelEncoder().default(TestModel.objects.all())
        for obj in TestModel.objects.all():
            self.assertIn({
                'testfield': obj.testfield,
                'id': obj.id,
            }, result, _('Serialize of qs not work!'))
        result = SpecialModelEncoder().default(TestModel2.objects.all())
        for obj in TestModel2.objects.all():
            self.assertIn({
                'testfield': obj.testfield,
                'testfield1': {
                    'testfield': obj.testfield1.testfield,
                    'id': obj.testfield1.id
                }, 'id': obj.id,
            }, result, _('Serialize of qs with foreign key not work!'))
