#!/usr/bin/env python
# encoding: utf-8
import traceback

from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
from time import time
import base64
from sqlalchemy.orm.exc import NoResultFound


class CacheHandler(tornado.web.HTTPRequest):

    def __init__(self, cachekind, cachetime, user):
        self.time = cachetime
        self.cache = cachekind
        self.user = user

    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        self.db.close()
