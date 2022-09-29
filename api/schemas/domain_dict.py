
from flask_restful import request
from marshmallow_sqlalchemy import  SQLAlchemyAutoSchema
from marshmallow import fields, post_load, ValidationError, validates, validates_schema
from api.models.domain import DomainModel, DomainGroupModel, DomainSslModel



class DomainSslSchema(SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    issuer = fields.Str()
    domain = fields.Str()
    tls_version = fields.Str()
    cert = fields.Str(required=True,  error_messages={
                      "required": "cert  cannot be empty"})
    key = fields.Str(required=True, error_messages={
                     "required": "key  cannot be empty"})
    start_date = fields.Str()
    expire_date = fields.Str()
    is_expired = fields.Str()
    describe = fields.Str()
    created_at = fields.DateTime(dt_format='iso8601', dump_only=True)
    updated_at = fields.DateTime(dt_format='iso8601', dump_only=True)

    @post_load
    def post_load(self, data, **kwargs):
        return DomainSslModel(**data)

    class Meta:
        model = DomainSslModel
        # exlude = ('cert', 'key',)
        # fields = ['id', 'title', 'describe', 'created_at', 'updated_at']





class DomainGroupSchema(SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, error_messages={
                       "required": "title cannot be empty"})
    created_at = fields.DateTime(dt_format='iso8601', dump_only=True)
    updated_at = fields.DateTime(dt_format='iso8601', dump_only=True)

    @validates("title")
    def validate_title(self, data, **kwargs):
        # 根据请求方式，自定义验证数据
        if request.method == "POST":
            if DomainGroupModel.query.filter_by(title=data).first() is not None:
                raise ValidationError(data + " is already exists")
            return data

    # 反序列化使用
    @post_load
    def post_load(self, data, **kwargs):
        return DomainGroupModel(**data)


    class Meta:
        model = DomainGroupModel       # 关联模型
        # include_fk = False              # 启用外键关系
        # include_relationships = False  # 模型关系外部关系属性
        # fields = ["id", "title", "created_at",
        #           "updated_at"]    # 返回指定的字段，如果不指定返回全部


class DomainSchema(SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    domain = fields.Str(required=True, error_messages={"required": "domain cannot be empty"})
    pc_addr = fields.Url(required=True, error_messages={"required": "PC addr Not a valid URL."})
    mobile_addr = fields.Url(error_messages={"invalid": "Mobile addr Not a valid URL."})
    is_points = fields.Bool(required=True, error_messages={"required": "points type cannot be empty"})    # 不填写，默认False
    is_ssl = fields.Bool(required=True, error_messages={"required": "ssl type cannot be empty"})       # 不填写，默认False
    ssl_id = fields.Int(load_only=True)
    ssl = fields.Nested(DomainSslSchema,  only=['id', 'domain', 'cert', 'key'])
    group = fields.Nested(DomainGroupSchema,  only=['id', 'title'])
    group_id = fields.Int(required=True, load_only=True, error_messages={"required": "group_id cannot be empty"})
    created_at = fields.DateTime(dt_format='iso8601', dump_only=True)
    updated_at = fields.DateTime(dt_format='iso8601', dump_only=True)

    @validates_schema
    def validate(self, data, **kwargs):
        # 入职设置了区分,那么移动端地址都必须携带
        if data['is_points'] and 'mobile_addr' not in data.keys():
            raise ValidationError('mobile address must be set in .')
        
        # 判断是否开启SSL,如果开启必须传入 SSL 证书 ID
        if data['is_ssl'] and 'ssl_id' not in data.keys():
            raise ValidationError('If you open https, you need to pass in the id of the certificate')
        return data

    @post_load
    def post_load(self, data, **kwargs):
        return DomainModel(**data)

    class Meta:
        model = DomainModel       # 关联模型
        ordered = True
        # include_fk = True        # 启用外键关系
        # include_relationships = True  # 模型关系外部关系属性
        # fields = ["id", "domain", "redirect_url", "group", "created_at",
        #           "updated_at"]    # 返回指定的字段，如果不指定返回全部


