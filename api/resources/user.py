from flask_restful import Resource, request, reqparse
from api.schemas import UserSchema
from api.models import UserModel
from api.utils.api_errors_code import ApiResponse
from sqlalchemy import or_
from marshmallow import ValidationError
from api.utils.auth import authenticate

user_schema = UserSchema()
users_schema = UserSchema(many=True)




# 用户只运行批量查询
class UserListAPI(Resource):

    decorators = [authenticate()]
    
    """ 资源验证 """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('search', type=str, required=False,location='args', trim=True, default=None)            # 分页页码, 默认为None
        self.reqparse.add_argument('page', type=int, required=False,location='args', default=1)            # 分页页码, 默认为1，
        self.reqparse.add_argument('page_size', type=int, required=False,location='args', default=20)    # 分页显示数量，可选 choices() 规定只能用几个数量
        #  choices=(50,100,200,500),
        super(UserListAPI, self).__init__()


    def get(self):
        '''批量查询'''
        """
        获取所有信息
        search： 如果存在搜索内容，搜索后分页，支持批量搜索，格式： http://10.11.9.246:8000/api/v1.0/users?page=1&page_size=2&search=admin2,admin3,admin
        page: 请求页
        page_size: 当前页面数量
        """
        args = self.reqparse.parse_args()
        search = args.get('search')
        page = args.get('page')
        page_size = args.get('page_size')


        if search and len(search.split(',')) > 0:        
            OR_ = or_( UserModel.username == s.replace(' ','') for s in search.split(','))
            obj = UserModel.query.filter(OR_)
            users = obj.paginate(page, page_size)
        else:
            users = UserModel.query.paginate(page, page_size)

        # <flask_sqlalchemy.Pagination object at 0x000001F02A6C94A8> 。实际用户存储在 users.items一个列表中
        result = users_schema.dump(users.items)


        return ApiResponse.SUCCESS(data=result,               
                                    total = users.total,
                                    current_page = users.page,
                                    total_pages = users.pages,
                                )



# 单条数据的增删改查
class UserAPI(Resource):

    decorators = [authenticate()]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # self.reqparse.add_argument('username', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        super(UserAPI, self).__init__()

    def get(self, id):
        user = UserModel.query.get_or_404(id)
        result = user_schema.dump(user)
        if user:
            return ApiResponse.SUCCESS(data=result)
        return ApiResponse.NotFoudError()

    def post(self):
        json_data = request.json
        # 判断是否有数据传入
        if json_data is None:
            return ApiResponse.ParameterException(msg="No json data")

        try:
            user = user_schema.load(json_data, partial=("id",))
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        user.save()
        result = user_schema.dump(user)
        return ApiResponse.SUCCESS(data=result)


    def put(self, id):
        # json_data = request.json
        # # 判断是否有数据传入
        # if json_data is None or 'password' not in json_data.keys():
        #     return ApiResponse.ParameterException()

        # _query = UserModel.query.get(id)
        # if _query:
        #     password = json_data['password']
        #     _query.hash_password(password)
        #     _query.update()
        #     result = user_schema.dump(_query)
        #     return ApiResponse.SUCCESS(data=result)
        # return ApiResponse.NotFoudError(msg='{0} id not found.')

        '''允许修改密码'''
        
        args = self.reqparse.parse_args()
        password = args['password']
        _query = UserModel.query.get(id)
        if _query:
            _query.hash_password(password)
            _query.update()
            result = user_schema.dump(_query)
            return ApiResponse.SUCCESS(data=result)
        return ApiResponse.NotFoudError()



    def delete(self, id):
        user = UserModel.query.get_or_404(id)
        if user:
            user.delete()
            return ApiResponse.SUCCESS()
        return ApiResponse.NotFoudError()
