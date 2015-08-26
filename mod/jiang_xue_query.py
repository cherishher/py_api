# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json
import traceback
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET
from cache.JiangQueryCache import JiangQueryCache 
from sqlalchemy.orm.exc import NoResultFound
from time import localtime, strftime, time

class jiang_queryHandler(tornado.web.RequestHandler):
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
            status = self.db.query(JiangQueryCache).filter(JiangQueryCache.number == user).one()
            if status.date > int(time())-40000 and status.text != '*':
                self.write(status.text)
                self.finish()
                return
        except NoResultFound:
            status = JiangQueryCache(number = user,text = '*',date = int(time()))
            self.db.add(status)
            try:
                self.db.commit()
            except:
                self.db.rollback()

        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        index_url = 'http://my.seu.edu.cn/index.portal'
        xue_login_url = 'http://xg.urp.seu.edu.cn/epstar/web/swms/mainframe/getmenu.jsp'
        xue_gong_url = 'http://xg.urp.seu.edu.cn/epstar/web/swms/mainframe/homeWithRoleSelector.jsp'
        get_url = 'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ&current.model.id=4si1f2d-20s3t1-f3cdywsn-1-f3cld7o9-7'
        main_apply_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSZ/T_JXJ_JXJXXB&tfile=XGMRMB/BGTAG&filter=T_JXJ_JXJXXB:SFTM=0%20and%20SFPGTM=0%20and%20SHZT!=99&page=T_JXJ_JXJXXB:curpage=1,pagesize=20&applycustom=yes&orderby=T_JXJ_JXJXXB:SQRQ%20desc"
        main_get_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSZ/T_JXJ_JXJXXB&tfile=XGMRMB/BGTAG_GAIN&filter=T_JXJ_JXJXXB:SHZT=99&page=T_JXJ_JXJXXB:curpage=1,pagesize=20&applycustom=yes&orderby=T_JXJ_JXJXXB:SQRQ%20desc"
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
                                             'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ&current.model.id=4si1f2d-20s3t1-f3cdywsn-1-f3cld7o9-7'},
                                    request_timeout=7)
                request_get = HTTPRequest(
                                    main_get_url,
                                    method = 'GET',
                                    headers={'Cookie':login_cookie,
                                             'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ&current.model.id=4si1f2d-20s3t1-f3cdywsn-1-f3cld7o9-7'},
                                    request_timeout=7)
                response1,response2 = yield [client.fetch(request_apply),client.fetch(request_get)]
                retjson['content_apply'] = self.deal_apply(response1.body)
                retjson['content_get'] = self.deal_get(response2.body)

                length1 = len(retjson['content_apply'])
                length2 = len(retjson['content_get'])
                data_all = []
                request_all = []
                for i in range(length1):
                    data = {
                    'mainobj':'SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJZLB',
                    'Fields':'T_JXJ_JXJZLB:JXJMC,WID',
                    'Filter':"T_JXJ_JXJZLB: JXJZLBM = '"+retjson['content_apply'][i]['name']+"'",
                    'OrderBy':'T_JXJ_JXJZLB:',
                    'CheckFP':'no'
                    }
                    data_all.append(data)
                    request = HTTPRequest(
                                            xml_url,
                                            method = 'POST',
                                            body = urllib.urlencode(data),
                                            headers={'Cookie':login_cookie},
                                            request_timeout=8)
                    request_all.append(request)
                for i in range(length2):
                    data = {
                    'mainobj':'SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJZLB',
                    'Fields':'T_JXJ_JXJZLB:JXJMC,WID',
                    'Filter':"T_JXJ_JXJZLB: JXJZLBM = '"+retjson['content_get'][i]['name']+"'",
                    'OrderBy':'T_JXJ_JXJZLB:',
                    'CheckFP':'no'
                    }
                    data_all.append(data)
                    request = HTTPRequest(
                                            xml_url,
                                            method = 'POST',
                                            body = urllib.urlencode(data),
                                            headers={'Cookie':login_cookie},
                                            request_timeout=8)
                    request_all.append(request)

                response = yield [client.fetch(i) for i in request_all]
                for i in range(length1):
                    tree = ET.fromstring(response[i].body)
                    retjson['content_apply'][i]['name']=tree[0][0].text
                for i in range(length2):
                    tree = ET.fromstring(response[i+length1].body)
                    retjson['content_get'][i]['name']=tree[0][0].text
                    
        except Exception,e:
            # print traceback.format_exc()
            # print str(e)
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
                    'name':'',
                    'term':item[6+14*i].text,
                    'apply_time':item[7+14*i].text,
                    'state':'',
                    'course':item[9+14*i].text
                }
                ret_content.append(temp)
            self.get_name_apply(content,ret_content)
            return ret_content
    def get_name_apply(self,content,ret_content):
        soup = BeautifulSoup(content)
        item = soup.findAll('script')
        script_count = len(item)
        all_item = (script_count-12)/4
        for i in range(all_item):
            name_cont = item[11+i*4].text
            state_cont = item[12+i*4].text

            index1 = state_cont.find('\"')
            index2 = state_cont.find('\"',index1+1)
            state = state_cont[index1+1:index2]
            if state=="-1":
                ret_content[i]['state'] = "不通过".decode('utf-8')
            elif state=="1":
                ret_content[i]['state'] = "待审核".decode('utf-8')
            elif state=="99":
                ret_content[i]['state'] = "通过".decode('utf-8')
            else:
                ret_content[i]['state'] = "审核中".decode('utf-8')

            index1 = name_cont.find('\"')
            index2 = name_cont.find('\"',index1+1)
            ret_content[i]['name'] = name_cont[index1+1:index2]
    def deal_get(self,content):
        soup = BeautifulSoup(content)
        item = soup.findAll('td',{'nowrap':'true'})
        count = len(item)
        all_item = (count)/17
        if count<17:
            return ''
        else:
            ret_content = []
            for i in range(all_item):
                temp = {
                    'name':'',
                    'term':item[5+17*i].text,
                    'apply_time':item[6+17*i].text,
                    'state':item[9+17*i].text,
                    'money':item[4+17*i].text
                }
                ret_content.append(temp)
            self.get_name_get(content,ret_content)
            return ret_content
    def get_name_get(self,content,ret_content):
        soup = BeautifulSoup(content)
        item = soup.findAll('script')
        script_count = len(item)
        all_item = len(ret_content)
        for i in range(all_item):
            name_cont = item[11+i*2].text
            index1 = name_cont.find('\"')
            index2 = name_cont.find('\"',index1+1)
            ret_content[i]['name'] = name_cont[index1+1:index2]