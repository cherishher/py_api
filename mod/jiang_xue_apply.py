# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json
import traceback
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET

class jiang_applyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)
        content = self.get_argument('content',default=None)
        print len(content)
        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        form_url = 'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/BDTAG&filter=T_JXJ_JXJXXB:1=2&opr=new&jxjzlbm=2552&sffdj=0&sfadjsq=0'
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
                    data = {
                        'filter':'T_JXJ_JXJXXB:1=2',
                        'jxjzlbm':'',
                        'mainobj':'SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB',
                        'opr':'new',
                        'sfadjsq':0,
                        'sffdj':0,
                        'tfile':'XGMRMB/BDTAG'
                    }
                    request = HTTPRequest(
                                        form_url,
                                        method = 'POST',
                                        body = urllib.urlencode(data),
                                        headers={'Cookie':login_cookie,
                                                 'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ_APPLY'},
                                        request_timeout=7)
                    response = yield client.fetch(request)
                    # retjson['content'] = self.deal(response1.body)
                    retjson['content'] = response.body

                    # length1 = len(retjson['content_apply'])
                    # length2 = len(retjson['content_get'])
                    # data_all = []
                    # request_all = []
                    # for i in range(length1):
                    #     data = {
                    #     'mainobj':'SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJZLB',
                    #     'Fields':'T_JXJ_JXJZLB:JXJMC,WID',
                    #     'Filter':"T_JXJ_JXJZLB: JXJZLBM = '"+retjson['content_apply'][i]['name']+"'",
                    #     'OrderBy':'T_JXJ_JXJZLB:',
                    #     'CheckFP':'no'
                    #     }
                    #     data_all.append(data)
                    #     request = HTTPRequest(
                    #                             xml_url,
                    #                             method = 'POST',
                    #                             body = urllib.urlencode(data),
                    #                             headers={'Cookie':login_cookie},
                    #                             request_timeout=8)
                    #     request_all.append(request)
                    # for i in range(length2):
                    #     data = {
                    #     'mainobj':'SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJZLB',
                    #     'Fields':'T_JXJ_JXJZLB:JXJMC,WID',
                    #     'Filter':"T_JXJ_JXJZLB: JXJZLBM = '"+retjson['content_get'][i]['name']+"'",
                    #     'OrderBy':'T_JXJ_JXJZLB:',
                    #     'CheckFP':'no'
                    #     }
                    #     data_all.append(data)
                    #     request = HTTPRequest(
                    #                             xml_url,
                    #                             method = 'POST',
                    #                             body = urllib.urlencode(data),
                    #                             headers={'Cookie':login_cookie},
                    #                             request_timeout=8)
                    #     request_all.append(request)

                    # response = yield [client.fetch(i) for i in request_all]
                    # print len(response)
                    # for i in range(length1):
                    #     tree = ET.fromstring(response[i].body)
                    #     retjson['content_apply'][i]['name']=tree[0][0].text
                    # for i in range(length2):
                    #     tree = ET.fromstring(response[i+length1].body)
                    #     retjson['content_get'][i]['name']=tree[0][0].text
                    
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


# http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSZ/T_JXJ_JXJZLB&tfile=XGMRMB/BGTAG_APPLY&filter=T_JXJ_JXJZLB:KTZT=1%20and%20SFKSQ=1%20and%20TO_CHAR(SYSDATE,%20'yyyy-MM-dd')%20between%20%20TO_CHAR(SQKSRQ,%20'yyyy-MM-dd')%20and%20TO_CHAR(SQJSRQ,%20'yyyy-MM-dd')%20and%20JXJZLBM%20in%20(select%20jxjzlbm%20from%20t_jxj_jxjzlb%20d%20where%20(select%20sum(a.slxd)%20from%20t_pub_e_detailnumlim%20a,t_jxj_jxjdjb%20b,t_xsjbxx_xsjbb%20c%20where%20a.slxdqbm=b.slxdqbm%20and%20b.jxjzlbm=d.jxjzlbm%20and%20a.jd=c.yxsh%20and%20c.xh='213131592'%20%20AND%20A.SLXD<>'-1'%20group%20by%20b.jxjzlbm)>0)%20OR%20jxjzlbm%20IN(SELECT%20f.jxjzlbm%20FROM%20T_JXJ_JXJDJB%20f%20WHERE%20f.jxjzlbm=jxjzlbm%20AND%20f.slxdqbm%20IS%20NULL%20AND%20KTZT%20=%201%20AND%20SFKSQ%20=%201%20AND%20TO_CHAR(SYSDATE,%20'yyyy-MM-dd')%20BETWEEN%20TO_CHAR(SQKSRQ,%20'yyyy-MM-dd')%20AND%20TO_CHAR(SQJSRQ,%20'yyyy-MM-dd'))