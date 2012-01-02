from functools import wraps
from glob import glob
import json
from pika.adapters.tornado_connection import TornadoConnection
import pika
import tornado
import os


class PikaClient(object):

    def __init__(self, host, queue):
        self.queue = queue
        self.host = host
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None
        self.callbacks = {}

    def connect(self):
        if self.connecting:
            return
        self.connecting = True
        self.connection = TornadoConnection(
            pika.ConnectionParameters(host=self.host),
            on_open_callback=self.on_connected
        )
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, chanel):
        self.channel = chanel
        self.channel.queue_declare(
            queue=self.queue,
            durable=True,
        )

    def on_basic_cancel(self, frame):
        self.connection.close()

    def on_closed(self, connection):
        tornado.ioloop.IOLoop.instance().stop()

    def send(self, body):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=json.dumps(body),
        )


def coffee2js(coffee_path, js_path):
    for name in glob(os.path.join(coffee_path, '*.coffee')):
        os.system('coffee -c -o %s %s ' % (js_path, name))

def haml2html(haml_path, html_path):
    for name in glob(os.path.join(haml_path, '*.haml')):
        os.system('haml %s %s ' % (name, name.replace(haml_path, html_path).replace('.haml', '.html')))

def sass2css(sass_path, css_path):
    for name in glob(os.path.join(sass_path, '*.sass')):
        os.system('sass %s %s ' % (name, name.replace(sass_path, css_path).replace('.sass', '.css')))

class Dict2Obj(object):
    def __init__(self, entries):
        self.__dict__.update(entries)


class StaticHandler(tornado.web.RequestHandler):
    pass

    @classmethod
    def create(cls, static):
        return '/' + static, type('StaticHandler', (cls,), {
            'static': static,
        })