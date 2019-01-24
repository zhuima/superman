# -*- coding: utf-8 -*-


import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True


    SUPERMAN_POST_PER_PAGE = 10
    SUPERMAN_MANAGE_POST_PER_PAGE = 15
    SUPERMAN_COMMENT_PER_PAGE = 15

    SUPERMAN_LOCALES = ['en_US', 'zh_Hans_CN']

    BABEL_DEFAULT_LOCALE = SUPERMAN_LOCALES[0]
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

    WTF_CSRF_SECRET_KEY = 'random key for form'

    
    WHOOSHEE_MIN_STRING_LEN = 1

    SUPERMAN_SLOW_QUERY_THRESHOLD = 1


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

