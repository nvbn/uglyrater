#!/usr/bin/python
# -*- coding: utf-8 -*-

ADMINS = (
    ('Vladimir Yakovlev', 'nvbn.rm@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default':{
        'ENGINE':   'postgresql_psycopg2',
        'NAME':     '',
        'USER':     '',
        'PASSWORD': '',
        'HOST':     '',
        'PORT':     '',
    }
}

INTERNAL_IPS = ('127.0.0.1',)

DEBUG = True
TEMPLATE_DEBUG = True

DEFAULT_FROM = "root@localhost"