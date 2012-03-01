#!/usr/bin/python
import hashlib
import os
import sys
sys.path.append('..')
import time
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen
import tornadio2
from tornadotools.route import Route
from uglyweb import settings
from uglyweb.base import BaseConnection, BaseHandler
from uglyweb.utils import PikaClient, coffee2js, haml2html, sass2css
from uglyweb.vk_mixin import VKMixin


@Route(r'/')
class IndexHandler(BaseHandler):
    def get(self):
        self.render('templates/index.html', VK_ID=self.settings['client_id'])


@Route(r'/ext/')
class ExtHandler(BaseHandler):
    def get(self):
        self.render('templates/ext.html', VK_ID=self.settings['client_id'])


@Route(r'/about/')
class AboutHandler(BaseHandler):
    def get(self):
        self.render('templates/about.html', VK_ID=self.settings['client_id'])


class VKHandler(BaseHandler, VKMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("code", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return

        self.authorize_redirect(
            client_id=self.settings["client_id"],
            redirect_uri=self.settings['vk_redirect'],
            extra_params={"response_type": "code",}
        )

    @tornado.web.asynchronous
    @tornado.gen.engine
    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Auth failed")
        uid = user['response'][0]['uid']
        yield tornado.gen.Task(self.db.auth.remove, {'uid': uid})
        yield tornado.gen.Task(self.db.auth.insert, {'uid': uid})
        (new_user,), error = yield tornado.gen.Task(self.db.auth.find_one, {'uid': uid})
        secret = hashlib.md5(new_user['_id']._ObjectId__id + self.settings['cookie_secret'] + str(uid))
        secret = secret.hexdigest()
        yield tornado.gen.Task(self.db.auth.update, {'uid': uid}, {
            '$set': {'secret': secret}
        })
        self.set_cookie("uid", str(uid))
        self.set_cookie('secret', str(secret))
        self.redirect("/")


class LogoutHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.set_cookie('uid', '')
        self.set_cookie('secret', '')
        self.redirect("/")


if __name__ == '__main__':
    pc = PikaClient(
        getattr(settings, 'PIKA_HOST', 'localhost'),
        getattr(settings, 'PIKA_QUEUE', 'uglyweb'),
    )
    current = os.path.dirname(__file__)
    BaseConnection.pc = pc
    router = tornadio2.TornadioRouter(BaseConnection)
    coffee2js('media/coffee/', 'media/js/')
    haml2html('haml/', 'templates/')
    sass2css('media/sass/', 'media/css/')
    application = tornado.web.Application(
        router.apply_routes(Route.routes()),
        debug=getattr(settings, 'DEBUG', True),
        socket_io_port=getattr(settings, 'PORT', 8080),
        flash_policy_port=843,
        flash_policy_file=os.path.join(current, 'flashpolicy.xml'),
        db_host=getattr(settings, 'DB_HOST', 'localhost'),
        db_port=getattr(settings, 'DB_PORT', 27017),
        db_name=getattr(settings, 'DB_NAME', 'uglyweb'),
        static_path='media/',
        static_url_prefix='/media/',
        client_id=settings.VK_ID,
        vk_redirect=getattr(settings, 'VK_REDIRECT', 'http://127.0.0.1:8080/login/'),
        client_secret=settings.VK_SECRET,
        cookie_secret=getattr(settings, 'SECRET', 'IwannaUSElocalhost'),
    )
    BaseConnection.application = application
    application.pika = pc
    socket_server = tornadio2.SocketServer(application, auto_start=False)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_timeout(time.time() + 0.1, application.pika.connect)
    ioloop.start()
