# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json,base64
import traceback
import requests
from cache.JiangListCache import JiangListCache
from bs4 import BeautifulSoup
from baseQuery import BaseQueryHandler

class jiang_listHandler(BaseQueryHandler):


    def get_current_user(self):
        return self.get_secure_cookie("user")

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        retjson = {}
        try:
            content = BaseQueryHandler.readFromCache(self, JiangListCache, 40000)
            if content == 'failed':
                url = 'http://my.seu.edu.cn/index.portal?.p=Znxjb20ud2lzY29tLnBvcnRhbC5zaXRlLnYyLmltcGwuRnJhZ21lbnRXaW5kb3d8ZjM0MDl8dmlld3xub3JtYWx8YWN0aW9uPWFwcGxpZWRRdWVyeQ__'
                retjson = BaseQueryHandler.base_get(self, url)
                if retjson['code'] == 200:
                    content = self.getJiangInfo(retjson['content'])
                    retjson['content'] = content
                    BaseQueryHandler.refreshCache(self,JiangListCache, json.dumps(retjson))
                    self.render('yjxj.html', content=content)
                else:
                    self.render('fail.html')
            else:
                content = json.loads(content)['content']
                self.render('yjxj.html', content=content)
        except Exception:
            traceback.print_exc()

    def getJiangInfo(self,content):
        jiangList = []
        soup = BeautifulSoup(content,'lxml')
        items = soup.find_all('div',attrs={'class':'isp-service-item-info'})
        if(items[1].find('div',attrs={'class':'jxjTitle'}) == None):
            return jiangList
        for item in items[1:]:
            jiangInfo={}
            jiangInfo['title'] = item.find('div',attrs={'class':'jxjTitle'}).text
            jiangInfo['level'] = item.find_all('div',attrs={'class':'jxjInfo'})[0].text[6:]
            jiangInfo['year'] = item.find_all('div',attrs={'class':'jxjInfo'})[1].text[5:]
            jiangInfo['money'] = item.find_all('div',attrs={'class':'jxjInfo'})[2].text[3:]
            jiangInfo['state'] = item.find_all('div',attrs={'class':'jxjInfo'})[3].text[5:].strip()
            jiangList.append(jiangInfo)
        return jiangList
