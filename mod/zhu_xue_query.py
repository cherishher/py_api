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

        #read from cache
        try:
            status=self.db.query(ZhuQueryCache).filter(ZhuQueryCache.number==user).one()
            if status.date > int(time())-40000 and status.text != '*' :
                self.write(status.text)
                self.finish()
                return
        except NoResultFound:
            status = ZhuQueryCache(number=user,text='*',date = int(time()))
            self.db.add(status)
            try:
                self.db.commit()
            except:
                self.sb.rollback()

        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        main_get_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/BGTAG_GAIN&filter=T_ZXJ_XX:SHZT=99&page=T_ZXJ_XX:curpage=1,pagesize=20&orderby=T_ZXJ_XX:SQRQ%20desc"
        main_apply_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/BGTAG&filter=T_ZXJ_XX:SFTM=0%20and%20SFPGTM=0%20and%20SHZT!=99&page=T_ZXJ_XX:curpage=1,pagesize=20&orderby=T_ZXJ_XX:SQRQ%20desc"
        xml_url = "http://xg.urp.seu.edu.cn/epstar/app/getxml.jsp?"
        retjson = {'code':200, 'content':'',"content_get":'',"content_apply":''}
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
                data = {
                        'mainobj':'SWMS/JXJSZ/T_JXJ_JXJXXB',
                        'tfile':'XGMRMB/BGTAG',
                        'filter':'T_JXJ_JXJXXB:SFTM=0 and SFPGTM=0 and SHZT!=99',
                        'page':'T_JXJ_JXJXXB:curpage=1,pagesize=20',
                        'applycustom':'yes',
                        'orderby':'T_JXJ_JXJXXB:SQRQ desc'
                    }
                request_apply = HTTPRequest(
                                        main_apply_url,
                                        method = 'GET',
                                        headers={'Cookie':login_cookie,
                                                 'Referer':' http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/BGTAG&filter=T_ZXJ_XX:SFTM=0%20and%20SFPGTM=0%20and%20SHZT!=99&page=T_ZXJ_XX:curpage=1,pagesize=20&orderby=T_ZXJ_XX:SQRQ%20desc'},
                                        request_timeout=7)
                request_get = HTTPRequest(
                                        main_get_url,
                                        method = 'GET',
                                        headers={'Cookie':login_cookie,
                                                 'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/KJ¤t.model.id=4si1f4f-sf0c9h-f43ns7jy-1-f43ns7wj-2'},
                                        request_timeout=7)
                response1,response2 = yield [client.fetch(request_apply),client.fetch(request_get)]
                retjson['content_apply'] = self.deal_apply(response1.body)
                retjson['content_get'] = self.deal_get(response2.body)
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


    def deal_apply(self,content):
        soup = BeautifulSoup(content)
        item = soup.findAll('td',{'nowrap':'true'})
        count = len(item)
        all_item = (count)/14
        if count<14:
            return ''
        else:
            ret_content = []
            for i in range(all_item):
                temp = {
                    'name':item[2+14*i].text,
                    'dengji':item[6+14*i].text,
                    'apply_time':item[7+14*i].text,
                    'state':item[8+i*14].text
                }
                ret_content.append(temp)
            return ret_content

    def deal_get(self,content):
        soup = BeautifulSoup(content)
        item = soup.findAll('td',{'nowrap':'true'})
        count = len(item)
        all_item = (count)/11
        if count<11:
            return ''
        else:
            ret_content = []
            for i in range(all_item):
                temp = {
                    'name':item[4+11*i].text,
                    'dengji':item[5+11*i].text,
                    'apply_time':item[7+11*i].text,
                    'money':item[6+11*i].text
                }
                ret_content.append(temp)
            return ret_content