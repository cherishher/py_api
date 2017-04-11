# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json,base64
import traceback
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET
from cache.ZhuQueryCache import ZhuQueryCache
from sqlalchemy.orm.exc import NoResultFound
from time import time,localtime,strftime
from auth import getCookie

class zhu_queryHandler(tornado.web.RequestHandler):
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

        # read from cache
        try:
            status = self.db.query(ZhuQueryCache).filter(ZhuQueryCache.number == user).one()
            if status.date > int(time())-40000 and status.text != '*':
                self.write(status.text)
                self.finish()
                return
        except NoResultFound:
            status = ZhuQueryCache(number = user,text = '*',date = int(time()))
            self.db.add(status)
            try:
                self.db.commit()
            except:
                self.db.rollback()
        BASE_URL = "http://my.seu.edu.cn/index.portal"
        Zhu_QUERY_URL = "http://my.seu.edu.cn/index.portal?.pn=p1064_p1067"
        retjson = {'code':200, 'content':''}

        try:
            ret = getCookie(self.db,user,password)
            if ret['code'] == 200:
                cookie = ret['content']
                client = AsyncHTTPClient()
                request = HTTPRequest(
                    url = Zhu_QUERY_URL,
                    method = "GET",
                    headers = {'Cookie':cookie},
                    request_timeout = 15
                    )
                response = yield client.fetch(request)
                soup = BeautifulSoup(response.body)
                li_item = soup.find('li',{'id':'one3'})
                data_url = BASE_URL + li_item['onclick'].split("'")[1]+"&pageIndex=1&pageSize=20"
                split_array = response.headers['Set-Cookie'].split(";")
                cookie = cookie.split(";")[0] + ";" + split_array[0]+";"+split_array[1].split(",")[1]
                request = HTTPRequest(
                    url = data_url,
                    method = "GET",
                    headers = {
                        'Cookie':cookie,
                        'Referer':'http://my.seu.edu.cn/index.portal?.pn=p1064_p1067',
                        'Host':'my.seu.edu.cn'
                        },
                    request_timeout = 8
                    )
                response = yield client.fetch(request)
                data_content = response.body
                retjson['content'] = self.deal_data(response.body)
            else:
                retjson = ret
        except Exception,e:
            with open('api_error.log','a+') as f:
                f.write(strftime('%Y%m%d %H:%M:%S in [api]', localtime(time()))+'\n'+str(str(e)+'\n[jiang_query]\t'+str(user)+'\nString:'+str(retjson)+'\n\n'))
            retjson['code'] = 500
            retjson['content'] = 'system error'
        ret = json.dumps(retjson, ensure_ascii=False, indent=2)
        self.write(ret)
        self.finish()

        # refresh cache
        if retjson['code'] == 200:
            status.date = int(time())
            status.text = ret
            self.db.add(status)
            try:
                self.db.commit()
            except Exception,e:
                self.db.rollback()

    def deal_data(self,html):
        soup = BeautifulSoup(html)
        div = soup.findAll('div',{'class':'isp-service-item-content'})
        div.pop(0)
        ret = []
        for item in div:
            div_item = item.findAll('div',{'class':'jxjInfo'})
            temp = {
                'name':item.find('div',{'class':'jxjTitle'}).text,
                'type':div_item[0].text[6:],
                'term':div_item[1].text[5:],
                'money':div_item[2].text[3:],
                'state':div_item[3].text[5:]
            }
            ret.append(temp)
        return ret