import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Subscriptions(SqlAlchemyBase):
    __tablename__ = 'subscriptions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    autor_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer
                                )
    user = orm.relation('User')