
from api.extensions import db, Redis
import json
from api.utils.api_errors_code import ApiResponse
from flask_restful import Resource,reqparse
from api.models import DomainModel
from api.schemas import DomainSchema
from api.utils.auth import authenticate
from urllib.parse import urlparse
from flask import redirect



domains_schema = DomainSchema(many=True)
domains_prefix = 'domains'  # redis hash 表




# 缓存数据
class DomianCachaAPI(Resource):
    # decorators = [authenticate()]
    # 局部权限
    # method_decorators = {
    #     'post': [authenticate()],
    #     'delete': [authenticate()],
    # }


    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('u', type=str, required=True, location='args',trim=True, default=None)            # 分页页码, 默认为None
        self.reqparse.add_argument('type', type=int, required=False, location='args',trim=True, default=1, choices=(0, 1))  # 1是PC,0是手机
        super(DomianCachaAPI, self).__init__()

    # http://localhost:8000/api/v1/domain/cache/?u=http://98.net/&p=/&type=1
    def get(self):
        # 先查询域名是否存在
        # query = DomainModel.query.filter_by(domain=domain).first()
        args = self.reqparse.parse_args()
        u = args.get('u')
        referType = args.get('type')

        url = urlparse(u)
        path = url.path      # 来源请求path路径 '/a/b'
        query = url.query    # 来源路径后的请求参数 'code=1&search=1&page=2'
        scheme = url.scheme  # 协议  https  || http
        netloc = url.netloc  # 来源  111.com
        
        if len(scheme) > 0 and len(netloc) > 0:
            result = Redis.hget(domains_prefix, url.netloc)


            # 1、判断是否存在
            if result is not None:
                result = json.loads(result) # 字符串转换成字典

                # 后缀路径及参数设置为变量
                back_path = path + '?' + query
                # 2、判断来源是是否http 和 是否开启 SSL 
                if scheme == 'http' and result['is_ssl']:
                    return redirect(scheme + 's://' + netloc + back_path)

                # 3、判断是否区分终端
                if result['is_points']:
                    # 如果是手机端，则走手机端路径
                    if referType == 0:
                        return redirect(result['mobile_addr'] + back_path, 301)
  
                # 如果不区分或者来源是PC端
                return redirect(result['pc_addr'] + back_path, 301)
            
            # 4、如果 Redis 无数据，则返回 404
            return ApiResponse.NotFoudError()


        # 请求来源，无法验证和获取，返回无效
        return ApiResponse.ParameterException(msg='Invalid for request.')


    # 生成 hash Cache
    def post(self):
        query = DomainModel.query.all()

        # query.group = query.relate_group
        # if query.is_ssl:
        #     query.ssl = query.relate_ssl

        for q in query:
            q.group = q.relate_group
            if q.is_ssl:
                q.ssl = q.relate_ssl

        domains_list = domains_schema.dumps(query)

        data = json.loads(domains_list)

        # 批量添加到 Redis,
        _r = Redis()._get_r()
        pipeline = _r.pipeline()
        for d in data:
            # hash,key,value
            pipeline.hset(domains_prefix, d["domain"], json.dumps(d))
        pipeline.execute()

        # Redis.write("test", json.dumps(data[0]))
        return ApiResponse.SUCCESS(data=domains_list)

    # 删除hash 缓存
    def delete(self):
        
        # 清除 domains　hash 表中的所有键值对
        try:
            Redis.delete(domains_prefix)
            return ApiResponse.SUCCESS()
        except Exception as e:
            return ApiResponse.ServerError(msg=e)


