from pika.adapters.tornado_connection import TornadoConnection
import pika
import tornado


class PikaClient(object):

    def __init__(self, host, queue):
        self.queue = queue
        self.host = host
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

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
            body=body,
        )
