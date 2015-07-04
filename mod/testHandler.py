# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re

class testHandler(tornado.web.RequestHandler):
    def get(self):
        # self.redirect('/api/checkPWD')
        self.write(self.request.headers)

    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.redirect('/api/checkPWD')
        # self.write("You wrote " + self.get_argument("message"))
    # def get(self):
    #     self.write('hello')

    # @tornado.web.asynchronous
    # @tornado.gen.engine
    # def post(self):
    #     login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
    #     index_url = 'http://my.seu.edu.cn/index.portal'
    #     client = AsyncHTTPClient()
    #     login_value = {
    #         'Login.Token1':'213131592',
    #         'Login.Token2':'lj084358',
    #         'goto':'http://my.seu.edu.cn/loginSuccess.portal',
    #         'gotoOnFail':'http://my.seu.edu.cn/loginFailure.portal'
    #     }
    #     request = HTTPRequest(
    #                         login_url,
    #                         method='POST',
    #                         body = urllib.urlencode(login_value),
    #                         request_timeout=7
    #                     )
    #     response = yield tornado.gen.Task(client.fetch, request)
    #     login_cookie = response.headers['Set-Cookie'].split(';')[0]

    #     headers = {
    #         'Cookie':login_cookie
    #     }

    #     index_request = HTTPRequest(
    #                                 index_url,
    #                                 headers = headers,
    #                                 method = 'GET',
    #                                 request_timeout = 7)
    #     index_response = yield tornado.gen.Task(client.fetch,index_request)

    #     self.write(index_response.body)
    #     self.write('test')
    #     self.finish()