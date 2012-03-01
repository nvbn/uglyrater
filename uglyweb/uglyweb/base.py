import tornadio2
import asyncmongo
import tornado


class BaseConnection(tornadio2.SocketConnection):

    def __init__(self, *args, **kwargs):
        super(BaseConnection, self).__init__(*args, **kwargs)
        self.uid = None
        self.timer = None
        self.skip = 50

    def on_close(self):
        if self.timer:
            self.timer.stop()

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(
                pool_id='uglyweb',
                host=self.application.settings['db_host'],
                port=self.application.settings['db_port'],
                dbname=self.application.settings['db_name']
            )
        return self._db

    @tornado.gen.engine
    def update(self):
        (profiles,), error = yield tornado.gen.Task(
            self.db.profiles.find, skip=self.skip,
            limit=100, sort=[('rate', -1)]
        )
        if self.uid:
            uids = map(lambda profile: profile['uid'], profiles)
            (rates,), error = yield tornado.gen.Task(
                self.db.rates.find, {
                    'who': self.uid,
                    'uid': {'$in': uids},
                }
            )
            rates = map(lambda rate: {
                'uid': rate['uid'],
                'value': int(rate['value']) + 1,
            }, rates)
        else:
            rates = []
        self.emit('update', map(lambda profile: {
            'first_name': profile['first_name'],
            'last_name': profile['last_name'],
            'photo': profile['photo'],
            'uid': profile['uid'],
            'rate': profile.get('rate', 0),
        }, profiles), rates)


    @tornadio2.event('subscribe')
    def subscribe(self):
        if not self.timer:
            self.timer = tornado.ioloop.PeriodicCallback(self.update, 1000)
            self.timer.start()

    @tornadio2.event('set_limits')
    def set_limits(self, skip, limit):
        self.skip = skip
        if limit > 100:
            limit = 100
        self.limit = limit

    @tornadio2.event('authorise')
    @tornado.gen.engine
    def authorise(self, uid, secret):
        user = None
        if uid and secret:
            (user,), error = yield tornado.gen.Task(self.db.auth.find_one, {
                'uid': int(uid),
                'secret': secret
            })
        self.emit('authorise_result', bool(user))
        self.update()
        if user:
            self.uid = int(uid)

    @tornadio2.event('set_rate')
    @tornado.gen.engine
    def set_rate(self, id, val):
        if self.uid:
            id = int(id)
            (rate,), error = yield tornado.gen.Task(
                self.db.rates.find_one, {
                    'who': self.uid,
                    'uid': id,
                }
            )
            allow = True
            num = 1
            if not rate:
                yield tornado.gen.Task(
                    self.db.rates.insert, {
                        'who': self.uid,
                        'uid': id,
                        'value': val,
                    }
                )
            elif rate and rate.get('value') != val:
                yield tornado.gen.Task(
                    self.db.rates.update, {
                        'who': self.uid,
                        'uid': id,
                    }, {
                        '$set': {'value': val}
                    }
                )
                num = 2
            else:
                allow = False
            if allow:
                yield tornado.gen.Task(self.db.profiles.update,{
                    'uid': id,
                }, {
                    '$inc': {'rate': num if val else -num}
                })
        self.update()

    @tornadio2.event('add')
    def add(self, url):
        if self.uid:
            self.pc.send({
                'url': url
            })
            self.update()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(
                pool_id='uglyweb',
                host=self.application.settings['db_host'],
                port=self.application.settings['db_port'],
                dbname=self.application.settings['db_name']
            )
        return self._db
