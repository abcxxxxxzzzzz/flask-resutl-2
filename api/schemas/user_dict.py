from flask_restful import request
from marshmallow_sqlalchemy import  SQLAlchemyAutoSchema
from marshmallow import fields, post_load, ValidationError, validates
from api.models.user import UserModel


# 用户表序列化
class UserSchema(SQLAlchemyAutoSchema):
    id = fields.Int(required=True, dump_only=True)
    username = fields.Str(required=True, error_messages={'required': "username for required."})
    password_hash = fields.Str(load_only=True)
    password = fields.Str(load_only=True, error_messages={'required': "password for required."})
    created_at = fields.DateTime(dt_format='iso8601', dump_only=True),
    updated_at = fields.DateTime(dt_format='iso8601', dump_only=True),

    @validates("username")
    def validate_username(self, value):
        # 根据请求方式，自定义验证数据
        if request.method == "POST":
            if UserModel.query.filter_by(username=value).first() is not None:
                raise ValidationError(value + " is already exists")

    # 注册反序列化对象后要调用的方法，它会在验证数据之后被调用。
    @post_load
    def post_load(self, data, **kwargs):
        if request.method == "POST":
            user = UserModel()
            user.username = data['username']
            user.hash_password(data['password'])
            data.pop('password')
            return user
        return UserModel(**data)

    class Meta:
        model = UserModel       # 关联模型
        # include_fk = False      # 启用外键关系
        # include_relationships = False  # 模型关系外部关系属性
        # fields = ["username", "id", "created_at","updated_at"]    # 返回指定的字段，如果不指定返回全部


