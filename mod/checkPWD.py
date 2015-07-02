# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json

class checkPwdHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)

        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        index_url = 'http://my.seu.edu.cn/index.portal'

        retjson = {'code':200, 'content':''}
        if not user or not password:
            retjson['code'] = 402
            retjson['content'] = 'params lack'
        else:
            try:
                client = AsyncHTTPClient()
                login_value = {
                    'Login.Token1':user,
                    'Login.Token2':password,
                    'goto':'http://my.seu.edu.cn/loginSuccess.portal',
                    'gotoOnFail':'http://my.seu.edu.cn/loginFailure.portal'
                }
                request = HTTPRequest(
                                    login_url,
                                    method='POST',
                                    body = urllib.urlencode(login_value),
                                    request_timeout=4
                                )
                response = yield tornado.gen.Task(client.fetch, request)
                if not response.headers:
                    retjson['code'] = 408
                    retjson['content'] = 'time out'
                else:
                    if response.body and response.body.find('Successed')>0:
                        print 'succeed'
                        login_cookie = response.headers['Set-Cookie'].split(';')[0]
                        retjson['content'] = login_cookie
                    else:
                       retjson['code'] = 400
                       retjson['content'] = 'wrong password' 
            except:
                retjson['code'] = 500
                retjson['content'] = 'system error'
                pass
        self.write(json.dumps(retjson, ensure_ascii=False, indent=2))
        self.finish()