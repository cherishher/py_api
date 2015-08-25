# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json
import traceback
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET

class zhu_listHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_argument('number',default=None)
        password = self.get_argument('password',default=None)

        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        index_url = 'http://my.seu.edu.cn/index.portal'
        main_get_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSZ/T_ZXJ_ZL&tfile=XGMRMB/BGTAG_APPLY&filter=T_ZXJ_ZL:KTZT=1%20and%20SFKSQ=1%20and%20(SQJSSJ%20is%20not%20null%20and%20%272015-08-24%27%3C=to_char(SQJSSJ,%27yyyy-mm-dd%27)%20and%20%272015-08-24%27%20%3E=%20to_char(SQKSSJ,%20%27yyyy-mm-dd%27))%20and%20(ZXJZLBM%20in%20(select%20ZXJZLBM%20from%20t_zxj_zl%20d%20where%20(select%20sum(a.slxd)%20from%20t_pub_e_detailnumlim%20a,t_zxj_dj%20b,t_xsjbxx_xsjbb%20c%20where%20(a.slxdqbm=b.slxdqbm%20or%20b.slxdqbm%20is%20null)%20and%20b.zxjzlbm=d.zxjzlbm%20and%20a.jd=c.yxsh%20and%20c.xh=%27213131150%27%20group%20by%20b.zxjzlbm)%3E0)%20or%20zxjzlbm%20in%20(select%20zxjzlbm%20from%20t_zxj_zl%20x,%20t_pub_filter_result%20y%20where%20(x.zgxdqbh%20=%20y.filterid%20or%20x.zgxdqbh%20is%20null)%20and%20y.xh%20=%20%27213131150%27))"
        # main_get_url = "http://mynew.seu.edu.cn/alone.portal?.pen=sw.qgzx&.ia=false&.pmn=view"
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
                                                 'Referer':' http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/ZXJGLZXT/ZXJSQ/T_ZXJ_XX&tfile=XGMRMB/KJ_APPLY'},
                                        request_timeout=7)
                    response = yield client.fetch(request)
                    retjson['content'] = self.deal(response.body)
                    # retjson['content'] = response.body
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
        all_item = (count)/11
        # this maybe 10 !!!!!!!
        if count<11:
            return ''
        else:
            ret_content = []
            for i in range(all_item):
                temp = {
                    'name':item[2+11*i].text,
                    'create_time':item[4+11*i].text,
                    'is_ok':item[5+11*i].text,
                    'pingdingzhouqi':item[6+11*i].text,
                    'fafangzhouqi':item[7+11*i].text,
                    'is_xiaowaishen':item[8+11*i].text,
                    'is_jijinhui':item[9+11*i].text
                }
                ret_content.append(temp)
            return ret_content