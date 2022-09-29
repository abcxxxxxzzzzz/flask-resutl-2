import os
from flask import Flask
from api.routes.routes import api_bp
from api.configs.config import config
from api.extensions import init_plugs

from flask_cors import CORS






# 传值 config_name, 设定运行环境(开发，测试，生产)
def create_app(config_name=None):
    app = Flask(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    if not config_name:
        # 尝试从本地环境中读取, 如果没有设置就设置为开发模式
        config_name = os.getenv('FLASK_CONFIG', 'development')

     # 引入数据库配置
    app.config.from_object(config[config_name])

    # 加载数据库
    # with app.app_context():
    # db.init_app(app=app)
    # Migrate(app, db)
    init_plugs(app)

    
    # 创建默认的账户,通过上下文的模式
    # from api.initialization.init import  init
    # with  app.app_context():
    #     init()

    # 注册使用flask_restful框架的路由, 并加上统一前缀
    app.register_blueprint(api_bp, url_prefix="/api/v1")


    # 加载欢迎语句
    # logo()

    #  解决跨域请求问题
    CORS(app, resources=r'/*')
    return app


def logo():
    print('''
            Welcome my api
    ''')
