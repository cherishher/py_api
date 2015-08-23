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
        par = self.get_argument('par',default=None)
        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        form_url = 'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/BDTAG&filter=T_JXJ_JXJXXB:1=2&opr=new&jxjzlbm=2552&sffdj=0&sfadjsq=0'
        post_yrl = 'http://xg.urp.seu.edu.cn/epstar/app/putxml.jsp?WebMethod=PutXml'
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

                    
                    # par['context'] = 
                    data = getXML(par)
                    request = HTTPRequest(
                                        post_url,
                                        method = 'POST',
                                        body = urllib.urlencode({'xmlparam':data}),
                                        headers={'Cookie':login_cookie,
                                                 'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ_APPLY'},
                                        request_timeout=7)
                    response = yield client.fetch(request)
                    # retjson['content'] = self.deal(response1.body)
                    retjson['content'] = response.body
            except Exception,e:
                print traceback.format_exc()
                print str(e)
                retjson['code'] = 500
                retjson['content'] = 'system error'
                pass
        self.write(json.dumps(retjson, ensure_ascii=False, indent=2))
        self.finish()
    def getXML(self,par):
        datatemp = """
        <GetXmlData>
        <document>
            <record state="new">
                <WID/>
                <SQBM>2zezbmqb-f7cv-uqht-gsl4-nxabjil73ni7</SQBM>
                <SFTM>0</SFTM>
                <SFPGTM>0</SFPGTM>
                <XH>213131592</XH>
                <XSH>71Y13123</XSH>
                <JXJZLBM>2552</JXJZLBM>
                <SQDJ>2490</SQDJ>
                <JE></JE>
                <JXJDJBM></JXJDJBM>
                <XN>2015</XN>
                <SQRQ>2015-07-03</SQRQ>
                <SQLY>12390kkoojhhgiuiooill</SQLY>
                <SHZT>1</SHZT>
                <SFYXWS>0</SFYXWS>
                <YX>100383</YX>
            </record>
                <Context BizObjName="T_JXJ_JXJXXB">
                <GetXml Control="editfield" Extension="" InnerData="maintain" IsSample="no" Session="mdPxh2VECyrkismVJXL1mKI" XmlType="metaxml">
                    <MainBizObj IDType="path">SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB</MainBizObj>
                    <ThisBizObj IDType="path">SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB</ThisBizObj>
                <Template>
                    <File IDType="">XGMRMB/BDTAG</File>
                    <Params>
                        <Param Name="sfadjsq">0</Param>
                        <Param Name="sffdj">0</Param>
                        <Param Name="filter" value="1=2">T_JXJ_JXJXXB:1=2</Param>
                        <Param Name="opr">new</Param><Param Name="jxjzlbm">2552</Param>
                    </Params>
                </Template>
                <ControlExt/>
                <Role>学生,所有用户</Role>
                <User>213131592</User>
                <IPAddr>223.3.4.175</IPAddr>
                </GetXml>
            </Context>
        </document>
        </GetXmlData>
        """

        data = """
        <GetXmlData>
        <document>
            <record state="new">
                
            </record>
                <Context BizObjName="T_JXJ_JXJXXB">
                
                </Context>
        </document>
        </GetXmlData>
        """

        root = ET.fromstring(data)

        root[0][0].extend(ET.fromstring(par['record']))
        root[0][1].extend(ET.fromstring(par['context']))
        return ET.tostring(root,encoding="utf-8")

