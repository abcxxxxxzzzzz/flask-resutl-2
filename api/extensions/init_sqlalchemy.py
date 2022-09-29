


from sqlalchemy import func
from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask import Flask
from flask_marshmallow import Marshmallow
# 封装 SQL 提交和 回滚


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True  # 声明当前类为抽象类，被继承，调用不会被创建
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.TIMESTAMP(True), comment="创建时间",
                           nullable=False, server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP(True), comment="更新时间",
                           nullable=False, server_default=func.now(), onupdate=func.now())


    def save(self):
        '''
        新增数据
        :return:
        '''
        db.session.add(self)
        db.session.commit()

    def update(self):
        '''
        更新数据
        :return:
        '''
        db.session.merge(self)
        db.session.commit()

    def delete(self):
        '''
        删除数据
        :return:
        '''
        db.session.delete(self)
        db.session.commit()

    def save_all(self, data):
        '''
        保存多条数据
        :param data:
        :return:
        '''
        db.session.execute(
            self.__table__.insert(),
            data
        )
        db.session.commit()


ma = Marshmallow()



def init_database(app: Flask):
    db.init_app(app)
    ma.init_app(app)
