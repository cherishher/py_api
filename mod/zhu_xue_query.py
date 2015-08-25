# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json
import traceback
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET

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


        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        # xue_login_url = 'http://xg.urp.seu.edu.cn/epstar/web/swms/mainframe/getmenu.jsp'
        # xue_gong_url = 'http://xg.urp.seu.edu.cn/epstar/web/swms/mainframe/homeWithRoleSelector.jsp'
        # get_url = 'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ&current.model.id=4si1f2d-20s3t1-f3cdywsn-1-f3cld7o9-7'
        main_get_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/BGTAG_GAIN&filter=T_ZXJ_XX:SHZT=99&page=T_ZXJ_XX:curpage=1,pagesize=20&orderby=T_ZXJ_XX:SQRQ%20desc"
        main_apply_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/BGTAG&filter=T_ZXJ_XX:SFTM=0%20and%20SFPGTM=0%20and%20SHZT!=99&page=T_ZXJ_XX:curpage=1,pagesize=20&orderby=T_ZXJ_XX:SQRQ%20desc"
        xml_url = "http://xg.urp.seu.edu.cn/epstar/app/getxml.jsp?"
        retjson = {'code':200, 'content':'',"content_get":'',"content_apply":''}
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
                    print login_cookie
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
                print traceback.format_exc()
                print str(e)
                retjson['code'] = 500
                retjson['content'] = 'system error'
                pass
        self.write(json.dumps(retjson, ensure_ascii=False, indent=2))
        self.finish()
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