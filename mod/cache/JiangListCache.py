#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : LiangJ
#@Data     : 2015-08-06 10:38

from sqlalchemy import Column, String, Integer, ForeignKey
from db import engine,Base

class JiangListCache(Base):
    __tablename__ = 'jianglist'
    number = Column(Integer, primary_key=True)
    text = Column(String(1024))
    date = Column(Integer, nullable=False)
