# from api.utils.db_base import BaseModel, db

# '''
# 参考： https://blog.csdn.net/qq_38796548/article/details/105704224
# '''
# # 用户角色中间表
# user_role = db.Table(
#     "user_role",
#     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
#     db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
# )

# # 角色权限中间表
# role_permission = db.Table(
#     "role_permission",
#     db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
#     db.Column("permission_id", db.Integer, db.ForeignKey("permission.id")),
# )

# # 用户表
# class UserModel(BaseModel):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(32), index=True)
#     password_hash = db.Column(db.String(128))
#     roles = db.relationship('RoleModel', secondary=user_role, back_populates='users')

# # 角色表


# class RoleModel(BaseModel):
#     __tablename__ = 'role'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(32))
#     permissions = db.relationship('PermissionModel', secondary=role_permission, back_populates='role')


# # 权限表(如增删改查)
# class PermissionModel(BaseModel):
#     __tablename__ = 'permission'
#     id = db.Column(db.Integer, primary_key=True)
#     url = db.Column(db.String(32))
#     title = db.Column(db.String(32))
#     permission_id = db.Column(db.Integer,  db.ForeignKey("permissiongroup.id"))
#     code = db.Column(max_length=32, default="")
#     parent = db.ForeignKey("self", default=1, null=True, blank=True)

# # 权限组表


# class PermissionGroupModel(BaseModel):
#     __tablename__ = 'permissiongroup'
#     id = db.Column(db.Integer, primary_key=True)
#     caption = db.Column(max_length=32)
#     permission_id = db.relationship('PermissionModel', backref=db.backref("permissions"))
#     menu = db.ForeignKey("MenuModel", default=1)


# # 菜单表
# class MenuModel(BaseModel):
#     __tablename__ = 'menu'
#     id = db.Column(db.Integer, primary_key=True)
#     sord_num = db.Integer(max_length=32)
#     caption = db.Column(max_length=32)
