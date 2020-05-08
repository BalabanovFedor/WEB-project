from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.clas import Clas

'''файл содержащий ресур можеди класса для api'''

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('school', required=True)


def abort_if_clas_not_found(user_id):
    session = db_session.create_session()
    user = session.query(Clas).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class ClasResource(Resource):
    def get(self, clas_id):
        abort_if_clas_not_found(clas_id)
        session = db_session.create_session()
        user = session.query(Clas).get(clas_id)
        return jsonify({'clas': user.to_dict(only=['id', 'school', 'name'])})

    def delete(self, clas_id):
        abort_if_clas_not_found(clas_id)
        session = db_session.create_session()
        user = session.query(Clas).get(clas_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class ClasListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(Clas).all()
        return jsonify({'clas': [item.to_dict(only=['id', 'school', 'name']) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if session.query(Clas).filter(Clas.name == args['name'], Clas.school == args['school']).all():
            return jsonify({'error': 'clas already exist'})
        user = Clas()
        user.name = args['name']
        user.school = args['school']

        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
