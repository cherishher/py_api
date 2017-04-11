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
from cache.JiangQueryCache import JiangQueryCache
from sqlalchemy.orm.exc import NoResultFound
from time import time,localtime,strftime
from cache.CookieCache import CookieCache
import requests
from baseQuery import BaseQueryHandler

class jiang_queryHandler(BaseQueryHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        retjson = {}
        try:
            content = BaseQueryHandler.readFromCache(self, JiangQueryCache , 40000)
            if content == 'failed':
                url = 'http://my.seu.edu.cn/index.portal?.p=Znxjb20ud2lzY29tLnBvcnRhbC5zaXRlLnYyLmltcGwuRnJhZ21lbnRXaW5kb3d8ZjM0MDl8dmlld3xtYXhpbWl6ZWR8YWN0aW9uPWxpc3Q_'
                retjson = BaseQueryHandler.base_get(self, url)
                if retjson['code'] == 200:
                    content = self.getJiangInfo(retjson['content'])
                    retjson['content'] = content
                    BaseQueryHandler.refreshCache(self,JiangQueryCache, json.dumps(retjson))
                    self.render('kjxj.html', content=content)
                else:
                    self.render('fail.html')
            else:
                content = json.loads(content)['content']
                self.render('kjxj.html', content=content)
        except Exception:
            traceback.print_exc()

    def getJiangInfo(self, content):
        jiangList = []
        soup = BeautifulSoup(content, 'lxml')
        items = soup.find_all('div', attrs={'class': 'isp-service-item-info'})
        if(items[0].find('div',attrs={'class':'jxjTitle'}) == None):
            return jiangList
        for item in items:
            jiangInfo = {}
            jiangInfo['title'] = item.find('div', attrs={'class': 'jxjTitle'}).text
            jiangInfo['time'] = item.find_all('div', attrs={'class': 'jxjInfo'})[0].text[3:].strip()
            jiangInfo['level'] = item.find_all('div', attrs={'class': 'jxjInfo'})[1].text[6:].strip()
            jiangInfo['year'] = item.find_all('div', attrs={'class': 'jxjInfo'})[2].text[5:].strip()
            jiangInfo['money'] = item.find_all('div', attrs={'class': 'jxjInfo'})[3].text[3:].strip()
            jiangList.append(jiangInfo)
        return jiangList
