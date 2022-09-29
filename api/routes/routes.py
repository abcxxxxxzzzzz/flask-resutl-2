from flask import Blueprint
from flask_restful import Api
from api.resources import LoginApi, LogoutApi
from api.resources import UserListAPI,UserAPI
from api.resources import DomainGroupAPI, DomainGroupListAPI, DomainAPI, DomainListAPI, SslAPI, SslListAPI, DomianCachaAPI




# 重写 handle_error（）函数, 交给全局异常处理
class RewriteApi(Api):
    def handle_error(self, e):
        raise e


# Blueprint('蓝图名字', import_name, 规则前缀)
api_bp = Blueprint('tasks', __name__)
api = RewriteApi(api_bp)


# Auth 路由
api.add_resource(LoginApi, '/auth/login',endpoint='login')    # 用户登录,返回 token
api.add_resource(LogoutApi, '/auth/logout',endpoint='logout') # 用户退出, Token 加入黑名单


# Users 路由
# [查询，批量查询，分页，添加用户]
api.add_resource(UserListAPI, '/users', endpoint='users')
api.add_resource(UserAPI, '/user', endpoint='add_user')       # 单个用户增加
api.add_resource(UserAPI, '/user/<int:id>', endpoint='user')  # 单个用户删、改、查
# api.add_resource(BatchAPI, '/users/batch', endpoint='users_batch')



# DomainsGroup 路由
api.add_resource(DomainListAPI, '/domains', endpoint='domains')
api.add_resource(DomainAPI, '/domain', endpoint='add_domain')     # 单个域名删、改、查
api.add_resource(DomainAPI, '/domain/<int:id>', endpoint='domain')     # 单个域名添加


# Domain 路由
api.add_resource(DomainGroupListAPI, '/domain/groups', endpoint='groups')
api.add_resource(DomainGroupAPI, '/domain/group', endpoint='add_group')
api.add_resource(DomainGroupAPI, '/domain/group/<int:id>', endpoint='group')



# SSL 路由
api.add_resource(SslListAPI, '/domain/ssls', endpoint='ssls')
api.add_resource(SslAPI, '/domain/ssl', endpoint='add_ssl')
api.add_resource(SslAPI, '/domain/ssl/<int:id>', endpoint='ssl')



# 刷新缓存

api.add_resource(DomianCachaAPI, '/domain/cache', endpoint='domain_cache')
