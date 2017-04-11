# -*- coding: utf-8 -*-
#@date  :2015-3-from

from sqlalchemy.orm import scoped_session, sessionmaker
from mod.auth import checkPwdHandler

from mod.jiang_xue_query import jiang_queryHandler
from mod.jiang_xue_apply import jiang_applyHandler
from mod.jiang_xue_list import jiang_listHandler

from mod.apply_infor import inforHandler

from mod.zhu_xue_query import zhu_queryHandler
from mod.zhu_xue_list import zhu_listHandler
# from mod.zzu_xue_apply import zhu_applyHandler

from mod.cache.db import engine
# from mod.user import User
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.gen
import os
# import check
import random



from tornado.options import define, options
define('port', default=8000, help='run on the given port', type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('signin.html')

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('home.html')

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
             (r'/',MainHandler),
             (r'/home',HomeHandler),
             (r'/api/checkPWD',checkPwdHandler),
             (r'/api/jiang_query',jiang_queryHandler),
             (r'/api/jiang_list',jiang_listHandler),
             (r'/api/jiang_apply',jiang_applyHandler),
             (r'/api/zhu_query',zhu_queryHandler),
             (r'/api/zhu_list',zhu_listHandler),
             (r'/api/info',inforHandler)
            ]
        settings = dict(
            cookie_secret="7CA71A57B571B5AEAC5E64C6042415DE",
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = scoped_session(sessionmaker(bind=engine,
                                              autocommit=False, autoflush=True,
                                              expire_on_commit=False))



if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()