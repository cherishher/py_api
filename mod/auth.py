# -*- coding: utf-8 -*-
# @Author  : jerry.liangj@qq.com
import traceback

from tornado.httpclient import HTTPRequest, AsyncHTTPClient,HTTPClient,HTTPError
from cache.CookieCache import CookieCache
import tornado.web
import tornado.gen
import urllib, re
import json,time
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm.exc import NoResultFound
from config import *

class checkPwdHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get(self):
        self.write('hello')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)
        result = {'code':200,'content':''}

        try:
            res = getCookie(self.db,user,password)
            if res['code'] == 200:
                self.set_secure_cookie('user', user)
            else:
                result = res
        except HTTPError:
            result['code'] = 400
        except Exception,e:
            result['code'] = 500
            result['content'] = str(e)
        self.write(json.dumps(result, ensure_ascii=False, indent=2))
        self.finish()

def getCookie(db,cardnum,card_pwd):
    state = 1
    ret = {'code':200,'content':''}
    try:
        result = db.query(CookieCache).filter(CookieCache.cardnum==cardnum).one()
        if (result.date+COOKIE_TIMEOUT<int(time.time())):
            code,cookie = RefreshCookie(cardnum,card_pwd)
            ret['content'] = cookie
            result.cookie = cookie
            result.date = int(time.time())
            try:
                db.add(result)
                db.commit()
            except:
                db.rollback()
        else:
            ret['content'] = result.cookie
    except NoResultFound:
        state = 0
    except Exception,e:
        ret['code'] = 500
        ret['content'] = str(e)
    if state==0:
        result = CookieCache(cardnum=cardnum,cookie="",date=int(time.time()))
        code,cookie = RefreshCookie(cardnum,card_pwd)
        if code == 200:
            ret['content'] = cookie
            result.cookie = cookie
            try:
                db.add(result)
                db.commit()
            except:
                db.rollback()
        else:
            ret['code'] = code
            ret['content'] = cookie
    return ret


def RefreshCookie(cardnum,card_pwd):
    try:
        response = requests.get(HOST_URL)
        soup =BeautifulSoup(response.content,'lxml')
        cookie = response.headers['Set-Cookie']
        cookie = cookie.split(",")[0] + ";" + cookie.split(",")[1].split(";")[0]

        elements = soup.find_all("input",attrs={'type':'hidden'})
        lt = elements[0]['value']
        dllt = elements[1]['value']
        execution = elements[2]['value']
        event_id = elements[3]['value']
        rmShown = elements[4]['value']

        data= {
            'username':cardnum,
            'password':card_pwd,
            'lt':lt,
            'dllt':dllt,
            'execution':execution,
            '_eventId':event_id,
            'rmShown':rmShown
        }

        headers = {
            'Referer':'http://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal',
            'Cookie':cookie
        }
        response = requests.post(HOST_URL,data = data, headers = headers, allow_redirects=False)
        keyCookie = response.headers['Set-Cookie'].split(";")[2].split(",")[1]
        headers = {
          'cookie': keyCookie.strip()
        }
        newUrl = response.headers['Location']
        response = requests.get(newUrl, headers = headers, allow_redirects=False)
        jsessionid_cookie = response.headers['Set-Cookie'].split(";")[0]
        login_cookie = keyCookie + ";" + jsessionid_cookie
        return 200,login_cookie
    except HTTPError:
        return 400,"password is not correct"
    except Exception,e:
        traceback.print_exc()
        return 500,'?>?'
