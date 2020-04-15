from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.homework import Homework

parser = reqparse.RequestParser()
parser.add_argument('subject', required=True)
parser.add_argument('content', required=True)
parser.add_argument('completion_date', required=True)
parser.add_argument('answer')
parser.add_argument('data')
parser.add_argument('user_id', required=True)


def abort_if_hw_not_found(user_id):
    session = db_session.create_session()
    user = session.query(Homework).get(user_id)
    if not user:
        abort(404, message=f"News {user_id} not found")


class HomeworkResource(Resource):
    def get(self, hw_id):
        abort_if_hw_not_found(hw_id)
        session = db_session.create_session()
        task = session.query(Homework).get(hw_id)
        return jsonify({'task': task.to_dict()})

    def delete(self, hw_id):
        abort_if_hw_not_found(hw_id)
        session = db_session.create_session()
        user = session.query(Homework).get(hw_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class HomeworkListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tasks = session.query(Homework).all()
        return jsonify({'tasks': [item.to_dict() for item in tasks]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        task = Homework()
        task.subject = args['subject']
        task.content = args['content']
        # task.completion_date = args['completion_date']
        # task.user_id = args['user_id']
        # task.clas_id = task.user.clas_id

        if args['answer']:
            task.answer = args['answer']
        if args['data']:
            task.answer = args['data']
        session.add(task)
        session.commit()
        return jsonify({'success': 'OK'})
