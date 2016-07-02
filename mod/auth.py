# -*- coding: utf-8 -*-
# @Author  : jerry.liangj@qq.com
from tornado.httpclient import HTTPRequest, AsyncHTTPClient,HTTPClient,HTTPError
from cache.CookieCache import CookieCache
import tornado.web
import tornado.gen
import urllib, re
import json,time
from sqlalchemy.orm.exc import NoResultFound
from config import *

class checkPwdHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)

        data = {
            'username':user,
            'password':password
        }
        result = {'code':200,'content':''}
        try:
            client = HTTPClient()
            request = HTTPRequest(
                CHECK_URL,
                method='POST',
                body=urllib.urlencode(data),
                validate_cert=False,
                request_timeout=TIME_OUT)
            response = client.fetch(request)
            header = response.headers
            if 'Ssocookie' in header.keys():
                headertemp = json.loads(header['Ssocookie'])
                cookie = headertemp[1]['cookieName']+"="+headertemp[1]['cookieValue']
                cookie += ";"+header['Set-Cookie'].split(";")[0]
                result['content'] = cookie
            else:
                result['code'] = 400
        except HTTPError:
            result['code'] = 400
        except Exception,e:
            result['code'] = 500
        self.write(json.dumps(result, ensure_ascii=False, indent=2))
        self.finish()

def getCookie(db,cardnum,card_pwd):
    state = 1
    ret = {'code':200,'content':''}
    try:
        result = db.query(CookieCache).filter(CookieCache.cardnum==cardnum).one()
        if (result.date+COOKIE_TIMEOUT<int(time.time())):
            state = 0
        else:
            ret['content'] = result.cookie
    except NoResultFound:
        result = CookieCache(cardnum=cardnum,cookie="",date=int(time.time()))
        state = 0
    except Exception,e:
        ret['code'] = 500
        ret['content'] = str(e)
    if state==0:
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
    data = {
            'username':cardnum,
            'password':card_pwd
        }
    try:
        client = HTTPClient()
        request = HTTPRequest(
            CHECK_URL,
            method='POST',
            body=urllib.urlencode(data),
            validate_cert=False,
            request_timeout=4)
        response = client.fetch(request)
        header = response.headers
        if 'Ssocookie' in header.keys():
            headertemp = json.loads(header['Ssocookie'])
            cookie = headertemp[1]['cookieName']+"="+headertemp[1]['cookieValue']
            cookie += ";"+header['Set-Cookie'].split(";")[0]
            return 200,cookie
        else:
            return 400,"No cookie"
    except HTTPError:
        return 400,"password is not correct"
    except Exception,e:
        return 500,str(e)