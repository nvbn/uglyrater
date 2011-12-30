#!/usr/bin/python
import json
import sys
sys.path.append('../../uglyweb/')
from uglyweb import settings
from pymongo import Connection
import fetch
import pika


class Fetcher(object):
    """Special fetcher"""

    def __init__(self, db_host, db_port, db_name, pika_host, pika_queue):
        """Init pymongo and pika"""
        self.connection = Connection(db_host, db_port)
        self.db = self.connection[db_name]
        self.p_conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=pika_host)
        )
        self.channel = self.p_conn.channel()
        self.channel.queue_declare(
            queue=pika_queue,
            durable=True
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.worker, queue=pika_queue)

    def run(self):
        """Start worker"""
        self.channel.start_consuming()

    def worker(self, ch, method, properties, body):
        """Pika callback"""
        data = json.loads(body)
        if 'url' in data:
            try:
                name = fetch.get_name_from_url(data['url'])
                profile = fetch.get_profile(name)
                profile['special'] = data.get('special', None)
                self.db.profiles.insert(profile)
            except fetch.ProfileNotFound:
                pass
        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )


def main():
    fetcher = Fetcher(
        db_host=getattr(settings, 'DB_HOST', 'localhost'),
        db_port=getattr(settings, 'DB_PORT', 27017),
        db_name=getattr(settings, 'DB_NAME', 'uglyweb'),
        pika_host=getattr(settings, 'PIKA_HOST', 'localhost'),
        pika_queue=getattr(settings, 'PIKA_QUEUE', 'uglyweb'),
    )
    fetcher.run()

if __name__ == '__main__':
    main()
