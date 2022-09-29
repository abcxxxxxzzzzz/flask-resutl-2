from flask_migrate import Migrate
import sys
import os

# 获取当前路径
# print(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)


from api import create_app
from api.extensions import db
from api.utils.api_errors_base import APIException

from werkzeug.exceptions import HTTPException




app = create_app()

migrate = Migrate(app, db)


@app.errorhandler(Exception)
def framework_error(e):
    # 判断异常是不是APIException
    if isinstance(e, APIException):
        return e
    # 判断异常是不是HTTPException
    if isinstance(e, HTTPException):
        code = e.code
        # 获取具体的响应错误信息
        msg = e.description
        error_code = 1007
        return APIException(code = code, msg = msg, error_code = error_code)
    # 异常肯定是Exception
    else:
        # 如果是调试模式,则返回e的具体异常信息。否则返回json格式的 APIException 对象！
        # 针对于异常信息，我们最好用日志的方式记录下来。
        # if app.config["DEBUG"]:
        #     return APIException()
        raise



# # 请求数据之前
# @app.before_request
# def process_request(*args, **kwargs):
#     # if request.path == '/login':
#     #     return None
#     # user = session.get('user_info')
#     # if user:
#     #     return None
#     # return redirect('/login')
#     print("======== 请求之前 ==========")
#     return None

# # 请求数据之后
# @app.after_request  # 后执行
# def process_response1(response):
#     print("======== 请求之后 ==========")
#     return response





if __name__ == '__main__':
    # app.wsgi_app = Middleware(app.wsgi_app)
    app.run()
