# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json,base64
import traceback
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from cache.JiangListCache import JiangListCache
from sqlalchemy.orm.exc import NoResultFound
from time import time,localtime,strftime
from config import AUTH_URL,INDEX_URL
import requests

class jiang_listHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
        
    def on_finish(self):
        self.db.close()

    def get(self):
        self.write('hello')
                                    
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)
        data = {
            'number':user,
            'password':password
        }

        # read from cache
        # try:
        #     status = self.db.query(JiangListCache).filter(JiangListCache.number == user).one()
        #     if status.date > int(time())-40000 and status.text != '*':
        #         self.write(status.text)
        #         self.finish()
        #         return
        # except NoResultFound:
        #     status = JiangListCache(number = user,text = '*',date = int(time()))
        #     self.db.add(status)
        #     try:
        #         self.db.commit()
        #     except:
        #         self.db.rollback()
		#


        retjson = {'code':200, 'content':''}
        try:
            client = AsyncHTTPClient()
            request = HTTPRequest(
                                AUTH_URL,
                                method = 'POST',
                                body = urllib.urlencode(data),
                                request_timeout=10)
            response = yield client.fetch(request)
            response = json.loads(response.body)
            if response['code'] != 200:
                retjson['code'] = 400
                retjson['content'] = 'wrong cardnum or password'
            else:
                cookie = response['content']
                main_get_url = 'http://my.seu.edu.cn/index.portal?.pn=p1064_p1551'
                request = HTTPRequest(
                                    main_get_url,
                                    method = 'GET',
                                    headers={'Cookie':cookie},
                                    request_timeout=15)
                response = yield client.fetch(request)
                body = response.body
                if not body:
                    retjson['code'] = 408
                    retjson['content'] = 'time out'
                # param = {'.p':self.getParam(body)}
                # request = HTTPRequest(
                #     url,
                #     method = 'GET',
                #     headers={'Cookie':cookie},
                #     request_timeout=15)
                # response = yield client.fetch(request)
                retjson['content'] = self.getJiangInfo(body)
        except Exception,e:
            # print traceback.format_exc()
            traceback.print_exc()
            with open('api_error.log','a+') as f:
                f.write(strftime('%Y%m%d %H:%M:%S in [api]', localtime(time()))+'\n'+str(str(e)+'\n[jiang_list]\t'+str(user)+'\nString:'+str(retjson)+'\n\n'))
            retjson['code'] = 500
            retjson['content'] = str(e)#'system error'
        ret = json.dumps(retjson, ensure_ascii=False, indent=2)
        self.write(ret)
        self.finish()

        # refresh cache
        # if retjson['code'] == 200:
        #     status.date = int(time())
        #     status.text = ret
        #     self.db.add(status)
        #     try:
        #         self.db.commit()
        #     except Exception,e:
        #         self.db.rollback()

    def getJiangInfo(self,content):
        jiangList = []
        jiangInfo = {
            'title':'',
            'level':'',
            'years':'',
            'money':'',
            'state':''
        }
        soup = BeautifulSoup(content,'lxml')
        items = soup.find_all('div',attrs={'class':'isp-service-item-info'})
        for item in items[1:]:
            jiangInfo['title'] = item.find('div',attrs={'class':'jxjTitle'}).text
            jiangInfo['level'] = item.find_all('div',attrs={'class':'jxjInfo'})[0].text[6:]
            jiangInfo['years'] = item.find_all('div',attrs={'class':'jxjInfo'})[1].text[5:]
            jiangInfo['money'] = item.find_all('div',attrs={'class':'jxjInfo'})[2].text[3:]
            jiangInfo['state'] = item.find_all('div',attrs={'class':'jxjInfo'})[3].text[5:].strip()
            jiangList.append(jiangInfo)
        return jiangList
