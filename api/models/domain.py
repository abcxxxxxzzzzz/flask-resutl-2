
from enum import unique
from api.extensions.init_sqlalchemy import db
from api.extensions import BaseModel

# tb_domain_ssl = db.Table('tb_domain_ssl', 
#                          db.Column("domain_id", db.Integer,
#                                    db.ForeignKey('domain.id')),
#                          db.Column("ssl_id", db.Integer,
#                                    db.ForeignKey('ssl.id')),
#                         )

# ssl tables

class DomainSslModel(BaseModel):
    __tablename__ = 'domain_ssl'
    issuer = db.Column(db.String(32))                   # 颁发机构
    domain = db.Column(db.String(1000), unique=True, index=True)                 # 证书归属域名,通过存入的时候获得
    tls_version = db.Column(db.String(32))              # 证书版本
    cert = db.Column(db.Text(), nullable=False)   # 证书 cert
    key = db.Column(db.Text(), nullable=False)    # 证书 key
    start_date = db.Column(db.String(32))               # 证书开始时间
    expire_date = db.Column(db.String(32))              # 证书到期时间
    is_expired=db.Column(db.Boolean())                    # 是否过期
    describe = db.Column(db.String(1000))               # 表述
    relate_domain = db.relationship("DomainModel", backref='relate_ssl', lazy='dynamic')


# domains tables
class DomainModel(BaseModel):
    __tablename__ = 'domain'
    domain = db.Column(db.String(32), nullable=False, unique=True, index=True)
    pc_addr = db.Column(db.String(32))                                # PC地址
    mobile_addr = db.Column(db.String(32))                            # 移动地址
    is_points = db.Column(db.Boolean(), default=False)                  # 是否区分PC和移动
    is_ssl = db.Column(db.Boolean(), default=False)                     # 是否开启 SSL 证书
    group_id = db.Column(db.Integer, db.ForeignKey("domain_group.id")) # 组ID
    ssl_id = db.Column(db.Integer, db.ForeignKey('domain_ssl.id'))
    # relate_ssl = db.relationship('SslModel', secondary=tb_domain_ssl, backref='relate_domain', lazy='dynamic')  # SSL 关联


# group tables
class DomainGroupModel(BaseModel):
    __tablename__ = 'domain_group'
    title = db.Column(db.String(32), nullable=False, unique=True, index=True)
    relate_domain = db.relationship("DomainModel", backref='relate_group', lazy='dynamic')


        
