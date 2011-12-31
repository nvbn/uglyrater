import tornadio2
import asyncmongo
import tornado


class BaseConnection(tornadio2.SocketConnection):
    def on_message(self, message):
        pass


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(
                host=self.application.settings['db_host'],
                port=self.application.settings['db_port'],
                dbname=self.application.settings['db_name']
            )
        return self._db
