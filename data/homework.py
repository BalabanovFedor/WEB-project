import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Homework(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'homework'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    clas_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('clas.id'))
    clas_obj = orm.relation('Clas')
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    completion_date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.String)
    data = sqlalchemy.Column(sqlalchemy.String)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def __repr__(self):
        return f"<Homework> {self.clas_id} {self.subject} {self.completion_date}"
