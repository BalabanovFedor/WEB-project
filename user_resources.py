from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.user import User
from data.clas import Clas

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password')
parser.add_argument('school', required=True)
parser.add_argument('clas', required=True)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict()})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(name=args['name'], email=args['email'])
        if args['password']:
            user.set_password(args['password'])
        if args['school'] and args['clas']:
            clas_id = session.query(Clas).filter(Clas.school == args['school'], Clas.name == args['clas']).first()
            if clas_id:
                user.clas_id = clas_id
            else:
                return jsonify({'error': 'not found school or class'})

        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
