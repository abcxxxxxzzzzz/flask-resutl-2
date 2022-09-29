
import logging
import os

class BaseConfig:
    # 是否开启 Google 令牌
    GOOGLE_ENABLE = int(os.getenv('GOOGLE_ENABLE') or 0)
    GOOGLE_KEY = os.getenv('GOOGLE_KEY') or "GOOGLE_KEY"
    GOOGLE_NAME = os.getenv('GOOGLE_NAME') or "sb"
    GOOGLE_ISSUER_NAME = os.getenv('ISSUER_NAME') or "sb"

    # JWT 令牌有效时间,默认三个小时
    EXPIRES_IN = 10800

    # 请求 API 携带头部信息                  
    AUTH_HEADER_NAME = 'X-Token'

    # # 增删改查是否立即提交，无需写db.session.commit()
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # JSON 配置
    JSON_AS_ASCII = False

    # 上传文件配置
    UPLOADED_PHOTOS_DEST = 'static/upload'
    UPLOADED_FILES_ALLOW = ['gif', 'jpg']

    # 加密秘钥
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    # redis配置
    REDIS_HOST = os.getenv('REDIS_HOST') or "127.0.0.1"
    REDIS_PORT = int(os.getenv('REDIS_PORT') or 6379)
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD') or ''
    REDIS_DB = int(os.getenv('REDIS_DB') or 0)
    REDIS_EXPIRE = int(os.getenv('REDIS_EXPIRE') or 0)

    # mysql 配置
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME') or "root"
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or "123456"
    MYSQL_HOST = os.getenv('MYSQL_HOST') or "127.0.0.1"
    MYSQL_PORT = int(os.getenv('MYSQL_PORT') or 3306)
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE') or "devops"

    # mysql 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    # 默认日志等级
    LOG_LEVEL = logging.WARN
    #
    MAIL_SERVER = os.getenv('MAIL_SERVER') or 'smtp.qq.com'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or '123@qq.com'
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or 'XXXXX'  # 生成的授权码

    # 默认发件人的邮箱,这里填写和MAIL_USERNAME一致即可
    MAIL_DEFAULT_SENDER = ('pear admin', os.getenv('MAIL_USERNAME') or '123@qq.com')


    @staticmethod
    def init_app(app):
        pass


class TestingConfig(BaseConfig):
    """ 测试配置 """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 内存数据库


class DevelopmentConfig(BaseConfig):
    """ 开发配置 """
    # 禁用事件警告
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    """生成环境配置"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 8

    LOG_LEVEL = logging.ERROR


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


# 解决中文编码的问题
config.update(RESTFUL_JSON = dict(ensure_ascii = False))


# ===================================
#  日志封装
# ====================================


# # 上传文件
# UPLOAD_HEAD_FOLDER = "static/uploads/avatar"
# app_url = "http://localhost:5000"


# def make_dir(make_dir_path):
#     """
#     文件生成
#     :param make_dir_path:
#     :return:
#     """
#     path = make_dir_path.strip()
#     if not os.path.exists(path):
#         os.makedirs(path)
#     return path


# log_dir_name = env.LOG_DIR_NAME  # 日志文件夹
# log_file_name = 'logger-' + \
#     time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'  # 文件名
# log_file_folder = os.path.abspath(os.path.join(os.path.dirname(
#     __file__), os.pardir, os.pardir)) + os.sep + log_dir_name
# make_dir(log_file_folder)

# log_file_str = log_file_folder + os.sep + log_file_name  # 输出格式
# log_level = env.LOG_LEVEL  # 日志等级

# handler = logging.FileHandler(log_file_str, encoding='UTF-8')
# handler.setLevel(log_level)
# logging_format = logging.Formatter(
#     '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
# handler.setFormatter(logging_format)
