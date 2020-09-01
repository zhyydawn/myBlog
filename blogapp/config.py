
# 数据库配置信息
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'

#DB_URL = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,DATABASE)

DB_URL = "{}+{}://{}:{}@{}:{}/".format(DIALECT,
                                       DRIVER, USERNAME, PASSWORD, HOST, PORT)
CHARSET = "?charset=utf8"

class Config:
    SECRET_KEY = "123456"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = 'FLASKY_ADMIN'
    TOKEN_EXPIRATION=7*24*3600 #配置token过期信息
    REDIS_PREFIX='token_auth_'
    REDIS_HOST = 'localhost'
    REDIS_PORT = '6379'
    REDIS_PASSWORD = 'root123'

    @staticmethod
    def init_app(app):
        pass

# 开发环境配置


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'MAIL_USERNAME'
    MAIL_PASSWORD = 'MAIL_PASSWORD'
    DATABASE = 'test'
    SQLALCHEMY_DATABASE_URI = DB_URL+DATABASE + CHARSET

# 测试环境配置


class TestingConfig(Config):
    TESTING = True
    DATABASE = 'test'
    SQLALCHEMY_DATABASE_URI = DB_URL+DATABASE + CHARSET

# 线上环境配置


class ProductionConfig(Config):
    DATABASE = 'test'
    SQLALCHEMY_DATABASE_URI = DB_URL+DATABASE + CHARSET


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
