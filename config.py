from os import path

basedir = path.abspath(path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'not-secure-secret-tk'
    APP_MODEL = './storage/ecdf7924eb6ba16cf1a8cdd4307e7d2f.hdf5'
    APP_TRUE = 'Dog'
    APP_FALSE = 'Cat'
    APP_THRESH = 0.5
    APP_PROXY = True


class ProtectedConfig(Config):
    APP_PROXY = True


class ProdConfig(Config):
    DEBUG = False


class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    APP_PROXY = True


class TestConfig(Config):
    TESTING = True
    APP_PROXY = True
