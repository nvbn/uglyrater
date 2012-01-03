#!/usr/bin/python
import json
import sys
from vkontakte.api import VKError

sys.path.append('../../uglyweb/')
from uglyweb import settings
from pymongo import Connection
import fetch
import pika
from logging import log


class Fetcher(object):
    """Special fetcher"""

    def __init__(self, db_host, db_port, db_name, pika_host, pika_queue, finished_queue):
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
        self.finished_queue = finished_queue

    def run(self):
        """Start worker"""
        self.channel.start_consuming()

    def worker(self, ch, method, properties, body):
        """Pika callback"""
        try:
            data = json.loads(body)
            name = data['name'] if data.get('name') else fetch.get_name_from_url(data['url'])
            if not self.db.profiles.find({
                '$or': [
                    {'uid': name},
                    {'screen_name': name}
                ]
            }).count():
                profile = fetch.get_profile(name)
                profile['rate'] = 0
                self.db.profiles.insert(profile)
        except (fetch.ProfileNotFound, KeyError, ValueError, VKError), e:
            log(0, e)
        finally:
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
        finished_queue=getattr(settings, 'FINISHED_QUEUE', 'finished')
    )
    fetcher.run()

if __name__ == '__main__':
    main()
