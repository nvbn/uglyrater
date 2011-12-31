#!/usr/bin/python
import unittest
import pymongo
import sys
import time
sys.path.append('../uglyweb/')
from uglyweb import settings
from random import randint
import json
from vk_fetcher import fetch
import pika


class FetcherTestCase(unittest.TestCase):
    """Test case for fetcher"""

    def setUp(self):
        """Set up pika and pymongo connection"""
        db_host = getattr(settings, 'DB_HOST', 'localhost')
        db_port = getattr(settings, 'DB_PORT', 27017)
        db_name = getattr(settings, 'DB_NAME', 'uglyweb')
        pika_host = getattr(settings, 'PIKA_HOST', 'localhost')
        self.pika_queue = getattr(settings, 'PIKA_QUEUE', 'uglyweb')
        conn = pymongo.Connection(db_host, db_port)
        self.db = conn[db_name]
        self.p_conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=pika_host)
        )
        self.channel = self.p_conn.channel()
        self.channel.queue_declare(
            queue=self.pika_queue,
            durable=True
        )

    def testSend(self):
        """Test pika send"""
        for i in range(20):
            self.assertEqual(None,
                self.channel.basic_publish(
                exchange='',
                routing_key=self.pika_queue,
                body=json.dumps({'ee': randint(1, 10000)}),
            ))

    def testVk(self):
        """Test getting profile from VK"""
        self.assertEqual(
            fetch.get_profile("fffffffffffffuuuuuuuuuuuuuuuuuuu"),
            fetch.get_profile("50025011"),
            'get from vk not work',
        )

    def testFetch(self):
        """Test getting name from url"""
        self.assertEqual(
            fetch.get_name_from_url(
                'http://vk.com/fffffffffffffuuuuuuuuuuuuuuuuuuu'
            ),
            'fffffffffffffuuuuuuuuuuuuuuuuuuu',
            'fetch from url not work'
        )

    def testNetworkFetch(self):
        """Test fetching profle by url via pika"""
        self.channel.basic_publish(
            exchange='',
            routing_key=self.pika_queue,
            body=json.dumps({
                'url': 'http://vk.com/fffffffffffffuuuuuuuuuuuuuuuuuuu/',
            }),
        )
        time.sleep(2)
        profile = self.db.profiles.find_one({
            '$or': [
                {'screen_name': "fffffffffffffuuuuuuuuuuuuuuuuuuu"},
                {'uid': "fffffffffffffuuuuuuuuuuuuuuuuuuu"}
            ]
        })
        profile.pop('_id')
        self.assertEqual(profile,
            fetch.get_profile("fffffffffffffuuuuuuuuuuuuuuuuuuu"),
            'fetch from network not work'
        )

if __name__ == '__main__':
    unittest.main()
