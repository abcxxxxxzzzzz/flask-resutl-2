
from flask_restful import Resource, reqparse
from api.models.user import BlacklistToken, UserModel
from api.utils.auth import get_header_token
from api.utils.auth import authenticate
from api.utils.api_errors_code import ApiResponse
from api.configs.config import BaseConfig
from api.extensions.init_GoogleAuthenticator import GoogleAuthenticatorClient


class LoginApi(Resource):

    def __init__(self):
        """ 资源验证 """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        self.reqparse.add_argument('code', type=str, location='json')
        super(LoginApi, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        # 判断是否开启了 Google 验证器
        if BaseConfig.GOOGLE_ENABLE:
            code = args.get('code',None)
            if code is None:
                return ApiResponse.GoogleError(msg='Please enter Google verification code.')

            # 验证 验证器 code 值
            res = GoogleAuthenticatorClient().verify_code_func(verify_code=code)
            if not res:
                return ApiResponse.AuthFailed(msg='Google verification code error.')

        username = args.get("username")
        password = args.get("password")
        user = UserModel.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return ApiResponse.AuthFailed()
        auth_token = user.generate_auth_token()
        return ApiResponse.SUCCESS(data={'token': auth_token.decode('ascii')})


class LogoutApi(Resource):

    '''退出'''

    decorators = [authenticate()]

    # 退出，token加入黑名单，实现过期
    def delete(self):
        auth_token = get_header_token()
        if auth_token:
            user = UserModel.verify_auth_token(auth_token)
            if user:
                blacklist_token = BlacklistToken(token=auth_token)
                blacklist_token.save()
                return ApiResponse.SUCCESS()
            else:
                return ApiResponse.AuthFailed()
        else:
            return ApiResponse.AuthFailed()
