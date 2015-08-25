# -*- coding: utf-8 -*-
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import urllib, re
import json,base64
import traceback
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET
from cache.JiangListCache import JiangListCache
from sqlalchemy.orm.exc import NoResultFound
from time import time

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
        
        # read from cache
        try:
            status = self.db.query(JiangListCache).filter(JiangListCache.number == user).one()
            if status.date > int(time())-40000 and status.text != '*':
                self.write(status.text)
                self.finish()
                return
        except NoResultFound:
            status = JiangListCache(number = user,text = '*',date = int(time()))
            self.db.add(status)
            try:
                self.db.commit()
            except:
                self.db.rollback()

        login_url = 'http://my.seu.edu.cn/userPasswordValidate.portal'
        index_url = 'http://my.seu.edu.cn/index.portal'
        main_get_url = "http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJSZ/T_JXJ_JXJZLB&tfile=XGMRMB/BGTAG_APPLY&filter=T_JXJ_JXJZLB:KTZT=1%20and%20SFKSQ=1%20and%20TO_CHAR(SYSDATE,%20'yyyy-MM-dd')%20between%20%20TO_CHAR(SQKSRQ,%20'yyyy-MM-dd')%20and%20TO_CHAR(SQJSRQ,%20'yyyy-MM-dd')%20and%20JXJZLBM%20in%20(select%20jxjzlbm%20from%20t_jxj_jxjzlb%20d%20where%20(select%20sum(a.slxd)%20from%20t_pub_e_detailnumlim%20a,t_jxj_jxjdjb%20b,t_xsjbxx_xsjbb%20c%20where%20a.slxdqbm=b.slxdqbm%20and%20b.jxjzlbm=d.jxjzlbm%20and%20a.jd=c.yxsh%20and%20c.xh='213131592'%20%20AND%20A.SLXD<>'-1'%20group%20by%20b.jxjzlbm)>0)%20OR%20jxjzlbm%20IN(SELECT%20f.jxjzlbm%20FROM%20T_JXJ_JXJDJB%20f%20WHERE%20f.jxjzlbm=jxjzlbm%20AND%20f.slxdqbm%20IS%20NULL%20AND%20KTZT%20=%201%20AND%20SFKSQ%20=%201%20AND%20TO_CHAR(SYSDATE,%20'yyyy-MM-dd')%20BETWEEN%20TO_CHAR(SQKSRQ,%20'yyyy-MM-dd')%20AND%20TO_CHAR(SQJSRQ,%20'yyyy-MM-dd'))"
        retjson = {'code':200, 'content':''}
        
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
                                             'Referer':'http://xg.urp.seu.edu.cn/epstar/app/template.jsp?mainobj=SWMS/JXJGLZXT/JXJSQ/T_JXJ_JXJXXB&tfile=XGMRMB/KJ_APPLY'},
                                    request_timeout=7)
                response = yield client.fetch(request)
                retjson['content'] = self.deal(response.body)
                # retjson['content'] = response.body
        except Exception,e:
            # print traceback.format_exc()
            # print str(e)
            with open('api_error.log','a+') as f:
                f.write(strftime('%Y%m%d %H:%M:%S in [api]', localtime(time()))+'\n'+str(str(e)+'\n[jiang_list]\t'+str(user)+'\nString:'+str(retjson)+'\n\n'))
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

    def deal(self,content):
        soup = BeautifulSoup(content)
        item = soup.findAll('td',{'nowrap':'true'})
        count = len(item)
        all_item = (count)/10
        if count<10:
            return ''
        else:
            ret_content = []
            for i in range(all_item):
                temp = {
                    'id':item[1+10*i]['pkvalue'],
                    'name':item[2+10*i].text,
                    'start_time':item[4+10*i].text,
                    'end_time':item[5+10*i].text,
                    'term':item[1+10*i]['pjxnvalue'],
                    'type':item[6+10*i].text
                }
                ret_content.append(temp)
            return ret_content