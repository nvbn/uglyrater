#!/usr/bin/python
import sys
sys.path.append('..')
import time
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornadio2
from uglyweb import settings
from uglyweb.base import BaseConnection
from uglyweb.utils import PikaClient, coffee2js


if __name__ == '__main__':
    router = tornadio2.TornadioRouter(BaseConnection)
    application = tornado.web.Application(
        router.urls,
        debug=getattr(settings, 'DEBUG', False),
        socket_io_port=getattr(settings, 'PORT', 8080),
        flash_policy_port=843,
        flash_policy_file='flashpolicy.xml',
        db_host=getattr(settings, 'DB_HOST', 'localhost'),
        db_port=getattr(settings, 'DB_PORT', 27017),
        db_name=getattr(settings, 'DB_NAME', 'uglyweb'),
    )
    coffee2js('media/coffee/', 'media/js/')
    pc = PikaClient(
        getattr(settings, 'PIKA_HOST', 'localhost'),
        getattr(settings, 'PIKA_QUEUE', 'uglyweb'),
    )
    application.pika = pc
    socket_server = tornadio2.SocketServer(application, auto_start=False)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_timeout(time.time() + .1, application.pika.connect)
    ioloop.start()
