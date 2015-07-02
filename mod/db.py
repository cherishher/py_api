# -*- coding: utf-8 -*-
from config import DB_URL
DB_HOST = DB_URL
DB_USER = 'root'
DB_PWD = '084358'
DB_NAME = 'api'

from sqlalchemy import create_engine

engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' %
                       (DB_USER, DB_PWD, DB_HOST, DB_NAME),
                       encoding='utf-8', echo=False,
                       pool_size=100, pool_recycle=10)