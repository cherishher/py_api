# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json
import traceback
from BeautifulSoup import BeautifulSoup

class inforHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)

        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        index_url = 'http://my.seu.edu.cn/index.portal'
        main_get_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/XSJBXX/T_XSJBXX_XSJBB&tfile=XGMRMB/detail_BDTAG&current.model.id=4si1f4g-ratw0e-f2oedbzc-1-f2of1hgj-6"
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
                                    request_timeout=7
                                )
                response = yield tornado.gen.Task(client.fetch, request)
                if not response.headers:
                    retjson['code'] = 408
                    retjson['content'] = 'time out'
                else:
                    login_cookie = response.headers['Set-Cookie'].split(';')[0]
                    request = HTTPRequest(
                                        main_get_url,
                                        method = 'GET',
                                        headers={'Cookie':login_cookie,
                                                 'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ_APPLY'},
                                        request_timeout=7)
                    response = yield client.fetch(request)
                    # retjson['content'] = response.body
                    retjson['content'] = self.deal(response.body)
            except Exception,e:
                print traceback.format_exc()
                print str(e)
                retjson['code'] = 500
                retjson['content'] = 'system error'
                pass
        self.write(json.dumps(retjson, ensure_ascii=False, indent=2))
        self.finish()
    def deal(self,content):
        soup = BeautifulSoup(content)
        return {
            'name':soup.find('font',{'id':'XM'}).text,
            'student_id':soup.find('font',{'id':'XSH'}).text,
            'course':soup.find('font',{'id':'ZYDM'}).text,
            'nianji':soup.find('font',{'id':'XZNJ'}).text,
            'tele':soup.find('font',{'id':'LXDH'}).text,
            'phone':soup.find('font',{'id':'SJH'}).text,
            'email':soup.find('font',{'id':'DZXX'}).text,
            'QQ':soup.find('font',{'id':'QQH'}).text
        }
        return ret_content
