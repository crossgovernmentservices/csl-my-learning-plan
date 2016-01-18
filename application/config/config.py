# -*- coding: utf-8 -*-
import os, json


class Config(object):
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    WTF_CSRF_ENABLED = True

    default_config_file_path = os.path.join(APP_ROOT, 'config.json')

    with open(os.environ.get('APP_CONFIG_FILE', default_config_file_path)) as app_config_file:
        app_config = json.load(app_config_file)

    SECRET_KEY = app_config.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_PASSWORD_HASH = app_config.get('SECURITY_PASSWORD_HASH', 'bcrypt')

    HOST = app_config.get('HOST', 'localhost')

    MONGODB_SETTINGS = {
        'host': app_config.get('MONGO_URI')
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = Config.SECRET_KEY or 'local-dev-not-secret'


class TestConfig(DevelopmentConfig):
    TESTING = True
