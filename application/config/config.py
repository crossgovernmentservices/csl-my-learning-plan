# -*- coding: utf-8 -*-
import os, json


class Config(object):
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    WTF_CSRF_ENABLED = True

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_PASSWORD_HASH = os.environ.get('SECURITY_PASSWORD_HASH', 'bcrypt')

    HOST = os.environ.get('HOST', 'localhost')

    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGO_URI')
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = Config.SECRET_KEY or 'local-dev-not-secret'


class TestConfig(DevelopmentConfig):
    TESTING = True
