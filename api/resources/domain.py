
from flask_restful import Resource, request, reqparse, marshal_with, fields, marshal
from api.models.domain import DomainModel, DomainGroupModel, DomainSslModel
from api.utils.api_errors_code import ApiResponse
from api.utils.check_ssl import check_cer
from sqlalchemy import or_
from api.extensions import db
from api.schemas import DomainSchema, DomainGroupSchema, DomainSslSchema
from marshmallow import  ValidationError
from api.utils.auth import authenticate



domain_schema = DomainSchema()
domains_schema = DomainSchema(many=True)
group_schema = DomainGroupSchema()
groups_schema = DomainGroupSchema(many=True)
Ssl_Schema = DomainSslSchema()
Ssls_Schema = DomainSslSchema(many=True)


reqparse = reqparse.RequestParser()
reqparse.add_argument('search', type=str, required=False,location='args', trim=True, default=None)            # 分页页码, 默认为None
reqparse.add_argument('page', type=int, required=False, location='args', default=1)            # 分页页码, 默认为1，
reqparse.add_argument('page_size', type=int, required=False, location='args', default=20) #  分页显示数量，可选 choices() 规定只能用几个数量choices=(50,100,200,500),

class DomainListAPI(Resource):

    decorators = [authenticate()]


    '''分页,批量查询'''
    def get(self):
        '''批量查询'''
        """
        获取所有信息
        search： 如果存在搜索内容，搜索后分页，支持批量搜索，格式： http://10.11.9.246:8000/api/v1.0/users?page=1&page_size=2&search=admin2,admin3,admin
        page: 请求页
        page_size: 当前页面数量
        """
        args = reqparse.parse_args()
        search = args.get('search')
        page = args.get('page')
        page_size = args.get('page_size')

        if search and len(search.split(',')) > 0:
            OR_ = or_(DomainModel.domain == s.replace(' ', '')for s in search.split(','))
            obj = DomainModel.query.filter(OR_)
            users = obj.paginate(page, page_size)
        else:
            users = DomainModel.query.paginate(page, page_size)

        # <flask_sqlalchemy.Pagination object at 0x000001F02A6C94A8> 。实际用户存储在 users.items一个列表中
        result = domains_schema.dump(users.items)

        return ApiResponse.SUCCESS(data=result,
                                   total=users.total,
                                   current_page=users.page,
                                   total_pages=users.pages,
                                   )

    '''批量添加'''
    def post(self):
        
        json_data = request.json
        if json_data is None:
            return ApiResponse.ParameterException()

        # 校验传入的 JSON 数组

        try:
            domains_list = domains_schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            _msg = list(_e.values())[0]
            msg = list(_msg.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        # 先判断所有域名是否有重复输入的
        old_list = [d.domain for d in domains_list]
        new_list = set(old_list)
        if len(old_list) != len(new_list):
            return ApiResponse.ParameterException(msg="Please remove duplicate domain names first.")

        # 批量查询域名是否存在, 如果存在就返回
        domain_exists = DomainModel.query.filter( or_(DomainModel.domain == d.domain for d in domains_list)).all()
        _msg = [e.domain for e in domain_exists ]
        if len(_msg) > 0:
            try:
                return ApiResponse.ParameterException(msg="{0} already is exists,Please check.".format(",".join(_msg)))
            except:
                return ApiResponse.ParameterException(msg="{0} already is exists,Please check.".format(_msg[0]))
        

        # 批量查询组 ID 是否存在, 通过差集的方式 如果不存在就返回
        id_set = list(set([g.group_id for g in domains_list]))
        group_exists = DomainGroupModel.query.filter(or_(DomainGroupModel.id == d for d in id_set)).all()
        _exists = [e.id for e in group_exists]
        _msg = list(set(id_set).difference(set(_exists)))
        if len(_msg) > 0:
            try:
                return ApiResponse.ParameterException(msg="{0} group id not have ,Please get id after create group.".format(",".join(_msg)))
            except:
                return ApiResponse.ParameterException(msg="{0} group id not have ,Please get id after create group.".format(_msg[0]))

        # 批量查询是否开启https, 如果开启，那么检测 SSL ID 是否存在，通过差集的方式 如果不存在就返回
        _ssl_id_set = list(set([g.ssl_id for g in domains_list if g.is_ssl ]))
        _ssl_exists = DomainSslModel.query.filter(or_(DomainSslModel.id == d for d in _ssl_id_set)).all()
        _ssl_id = [e.id for e in _ssl_exists]
        _msg = list(set(_ssl_id_set).difference(set(_ssl_id)))
        if len(_msg) > 0:
            try:
                return ApiResponse.ParameterException(msg="{0} ssl id not have ,Please get id after create ssl.".format(",".join(_msg)))
            except:
                return ApiResponse.ParameterException(msg="{0} ssl id not have ,Please get id after create ssl.".format(_msg[0]))

        # 批量添加
        db.session.bulk_save_objects(domains_list)
        db.session.commit()
        return ApiResponse.SUCCESS(msg="Batch added successfully")

    def put(self):
        # 通过判断 ?type=xxx 类型，来决定更新的内容
        pass

    '''批量删除'''
    def delete(self):
        '''待修改, [7,8] 列表形式'''
        json_data = request.json


        if json_data is None:
            return ApiResponse.ParameterException()

        if len(json_data) <= 1:
            return ApiResponse.ParameterException(msg="Less than or equal to one piece of data, please delete it separately")

        if not isinstance(json_data, list):
            return ApiResponse.ParameterException('Batch delete must be list')

        try:
            DomainModel.query.filter(DomainModel.id.in_(json_data)).delete()
            return ApiResponse.SUCCESS()
        except Exception as e:
            db.session.rollback()
            return ApiResponse.ParameterException(msg='Batch delete error.')

# 单条数据的增删改查
class DomainAPI(Resource):
    
    # decorators = [authenticate()]

    def get(self, id):
        query = DomainModel.query.get_or_404(id)
        query.group = query.relate_group
        if query.is_ssl:
            query.ssl = query.relate_ssl
        resutl = domain_schema.dump(query)
        return ApiResponse.SUCCESS(data=resutl)

    def post(self):
        # 只需要传入 title 名称
        json_data = request.json
        
        # 判断是否有数据传入
        if json_data is None:
            return ApiResponse.ParameterException(msg="No json data")

        # 反序列化传入的数据
        try:
            _inDB = domain_schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        # 判断添加的域名是否存在
        if DomainModel.query.filter_by(domain = _inDB.domain).first():
            return ApiResponse.ParameterException(msg=_inDB.domain + ' is aready exists')

        # 判断关联的组 ID 是否存在
        group = DomainGroupModel.query.filter_by(id=_inDB.group_id).first()

        # 判断是否开启SSL
        if _inDB.is_ssl:
            ssl = DomainSslModel.query.filter_by(id=_inDB.ssl_id).first()
            if ssl is None:
                return ApiResponse.ParameterException('The ssl id not found.')

        # 判断是否开启了证书，如果开启了证书，查询证书ID是否存在
        if group:
            _inDB.save()
            _inDB.group = group
            if _inDB.is_ssl:
                _inDB.ssl = ssl

            # 返回 JSON 数据给前端
            resutl = domain_schema.dump(_inDB)
            return ApiResponse.SUCCESS(data=resutl)
        return ApiResponse.ServerError(msg='The group id not found.')

    def put(self, id):
        json_data = request.json
        if json_data is None:
            return ApiResponse.ParameterException(msg="No json data")

        # 反序列化验证传入的数据
        try:
            group = domain_schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        _query = DomainModel.query.get_or_404(id)

        # 如果域名重复,则报错
        try:
            _query.domain = group.domain
            _query.pc_addr = group.pc_addr
            _query.mobile_addr = group.mobile_addr
            _query.is_points = group.is_points
            _query.is_ssl = group.is_ssl
            _query.group_id = group.group_id
            _query.update()
        except Exception as e:
            return ApiResponse.ParameterException(msg='Update domain name already exists.')

        # 返回修改后的 JSON 数据给前端
        resutl = domain_schema.dump(_query)
        return ApiResponse.SUCCESS(data=resutl)
    
    def delete(self, id):
        _query = DomainModel.query.get_or_404(id)
        if _query:
            _query.delete()
            return ApiResponse.SUCCESS()
        return ApiResponse.NotFoudError()







class DomainGroupListAPI(Resource):

    decorators = [authenticate()]

    def get(self):
        args = reqparse.parse_args()
        search = args.get('search')
        page = args.get('page')
        page_size = args.get('page_size')

        if search and len(search.split(',')) > 0:
            OR_ = or_(DomainGroupModel.title == s.replace(' ', '')
                      for s in search.split(','))
            obj = DomainGroupModel.query.filter(OR_)
            _query = obj.paginate(page, page_size)
        else:
            _query = DomainGroupModel.query.paginate(page, page_size)

        # <flask_sqlalchemy.Pagination object at 0x000001F02A6C94A8> 。实际用户存储在 users.items一个列表中
        result = groups_schema.dump(_query.items)

        return ApiResponse.SUCCESS(data=result,
                                   total=_query.total,
                                   current_page=_query.page,
                                   total_pages=_query.pages,
                                   )

# 单条数据的增删改查
class DomainGroupAPI(Resource):

    decorators = [authenticate()]

    def get(self, id):
        query = DomainGroupModel.query.get_or_404(id)
        resutl = group_schema.dump(query)
        return ApiResponse.SUCCESS(data=resutl)

    def post(self):
        # 只需要传入 title 名称
        json_data = request.json
        
        # 判断是否有数据传入
        if json_data is None:
            return ApiResponse.ParameterException(msg="No json data")

        # 反序列化传入的数据
        try:
            _inDB = group_schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        # 保存序列化数据
        _inDB.save()

        # 返回 JSON 数据给前端
        resutl = group_schema.dump(_inDB)
        return ApiResponse.SUCCESS(data=resutl)

    def put(self, id):
        json_data = request.json
        if json_data is None:
            return ApiResponse.ParameterException(msg="No json data")

        # 反序列化传入的数据
        try:
            group = group_schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        _query = DomainGroupModel.query.get_or_404(id)

        try:
            _query.title = group.title
            _query.update()
        except Exception as e:
            return ApiResponse.ParameterException(msg='The updated name already exists.')

        # 返回修改后的 JSON 数据给前端
        resutl = group_schema.dump(_query)
        return ApiResponse.SUCCESS(data=resutl)

    def delete(self, id):
        _query = DomainGroupModel.query.get_or_404(id)
        if _query:
            _query.delete()
            return ApiResponse.SUCCESS()
        return ApiResponse.NotFoudError()











class SslListAPI(Resource):

    decorators = [authenticate()]

    def get(self):
        args = reqparse.parse_args()
        search = args.get('search')
        page = args.get('page')
        page_size = args.get('page_size')

        if search and len(search.split(',')) > 0:
            OR_ = or_(DomainSslModel.title == s.replace(' ', '')
                      for s in search.split(','))
            obj = DomainSslModel.query.filter(OR_)
            _query = obj.paginate(page, page_size)
        else:
            _query = DomainSslModel.query.paginate(page, page_size)

        # <flask_sqlalchemy.Pagination object at 0x000001F02A6C94A8> 。实际用户存储在 users.items一个列表中
        result = Ssls_Schema.dump(_query.items)

        return ApiResponse.SUCCESS(data=result,
                                   total=_query.total,
                                   current_page=_query.page,
                                   total_pages=_query.pages,
                                   )


class SslAPI(Resource):

    decorators = [authenticate()]

    def get(self, id):
        _query = DomainSslModel.query.get_or_404(id)
        resutl = Ssl_Schema.dump(_query)
        return ApiResponse.SUCCESS(data=resutl)

    def post(self):
        '''
            cert, key 原证书内容复制出来后把 \n 需要转换成 \r\n,然后再传输到后端
        '''
        json_data = request.json
        if json_data is None:
            return ApiResponse.ParameterException()

        try:
            _inDB = Ssl_Schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)

        _is_ssl = check_cer(_inDB.cert)
 
        # 先判断证书是否有效
        if not _is_ssl:
            return ApiResponse.ParameterException(msg='The SSL cert is invalid.')

        # 再判断否到期
        if _is_ssl['is_expired']:
            return ApiResponse.ParameterException(msg='The SSL cert is expired.')

        # 最后判断数据库中是否已经存在这个证书,通过主键判断
        _is_exists = DomainSslModel.query.filter_by(domain=_is_ssl['domain']).first()
        if _is_exists:
            return ApiResponse.ParameterException(msg='The domain ssl is exists; Please delete old ssl cert.')

        _inDB.issuer = _is_ssl['issuer']
        _inDB.domain = _is_ssl['domain']
        _inDB.tls_version = _is_ssl['tls_version']
        _inDB.start_date = _is_ssl['start_date']
        _inDB.expire_date = _is_ssl['expire_date']
        _inDB.is_expired = _is_ssl['is_expired']
        _inDB.save()
        return ApiResponse.SUCCESS(data=Ssl_Schema.dump(_inDB))

    def put(self, id):
        json_data = request.json
        if json_data is None:
            return ApiResponse.ParameterException()

        

        try:
            _inDB = Ssl_Schema.load(json_data)
        except ValidationError as err:
            _e = err.messages
            msg = list(_e.values())[0][0]
            return ApiResponse.ParameterException(msg=msg)


        _is_ssl = check_cer(_inDB.cert)

        # 先判断证书是否有效
        if not _is_ssl:
                return ApiResponse.ParameterException(msg='The update SSL cert is invalid.')

        # 再判断否到期
        if _is_ssl['is_expired']:
            return ApiResponse.ParameterException(msg='The update SSL cert is expired.')

        _query = DomainSslModel.query.get_or_404(id)

        try:
            _query.issuer = _is_ssl['issuer']
            _query.domain = _is_ssl['domain']
            _query.tls_version = _is_ssl['tls_version']
            _query.start_date = _is_ssl['start_date']
            _query.expire_date = _is_ssl['expire_date']
            _query.is_expired = _is_ssl['is_expired']
            _query.update()
        except Exception as e:
            return ApiResponse.ParameterException(msg='The updated ssl domain already exists.Please delete old domain ssl')

        # 返回修改后的 JSON 数据给前端
        resutl = Ssl_Schema.dump(_query)
        return ApiResponse.SUCCESS(data=resutl)

    def delete(self, id):
        _query = DomainSslModel.query.get_or_404(id)
        if _query:
            _query.delete()
            return ApiResponse.SUCCESS()
        return ApiResponse.NotFoudError()





