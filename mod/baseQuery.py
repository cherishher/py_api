#!/usr/bin/env python
# encoding: utf-8

"""
@version: python2.7.1
@author: MaxNeverBomb
@file: baseQuery.py
@time: 2017/4/8 下午5:07
"""
# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json, base64
import traceback
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from cache.JiangListCache import JiangListCache
from sqlalchemy.orm.exc import NoResultFound
from time import time, localtime, strftime
from cache.CookieCache import CookieCache
import requests


class BaseQueryHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        self.db.close()

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def base_get(self, url):
        retjson = {
            'content': '',
            'code': 200
        }
        if self.get_current_user():
            user = self.current_user
            pass
        else:
            self.redirect('/')
            return
        try:
            cookie = self.db.query(CookieCache).filter(CookieCache.cardnum == user).one()
            main_get_url = url
            body = requests.get(main_get_url, headers={'Cookie': cookie.cookie.strip()}).content
            if not body:
                retjson['code'] = 408
                retjson['content'] = 'time out'
            retjson['content'] = body
        except Exception, e:
            traceback.print_exc()
            retjson['code'] = 500
            retjson['content'] = 'system error'

        return retjson


    def readFromCache(self, cachekind, cachetime):
        # read from cache
        content = ''
        try:
            status = self.db.query(cachekind).filter(cachekind.number == self.current_user).one()
            if status.date > int(time()) - cachetime and status.text != '*':
                content = base64.b64decode(status.text)
                return content
            else:
                return 'failed'
        except NoResultFound:
            status = cachekind(number = self.current_user, text='*', date=int(time()))
            self.db.add(status)
            try:
                self.db.commit()
            except:
                self.db.rollback()
            return 'failed'


    def refreshCache(self,cachekind, content):
        #refresh cache
        try:
            status = self.db.query(cachekind).filter(cachekind.number == self.current_user).one()
            status.date = int(time())
            status.text = base64.b64encode(content)
            self.db.add(status)
            try:
                self.db.commit()
            except Exception,e:
                print str(e)
                self.db.rollback()
        except Exception,e:
            traceback.print_exc()