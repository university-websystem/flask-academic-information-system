from flask import request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from .. import db

# 사용자 정보 CRUD
# 사용자 관련 네임스페이스
ns_users = Namespace('users', description='사용자 정보 CRUD')

# 사용자 모델
user_model = ns_users.model('User', {
    'id': fields.String(required=True, description='학번(직번)'),
    'role': fields.String(required=True, description='역할'),
    'name': fields.String(required=True, description='이름'),
    'department': fields.String(description='학과'),
    'admission_year': fields.Integer(required=True, description='입학년도(고용년도)')
})

register_model = ns_users.model('Register', {
    'id': fields.String(required=True, description='학번(직번)'),
    'password': fields.String(required=True, description='비밀번호'),
    'role': fields.String(required=True, description='역할'),
    'name': fields.String(required=True, description='이름'),
    'department': fields.String(description='학과'),
    'admission_year': fields.Integer(required=True, description='입학년도(고용년도)')
})

# Create, Read
@ns_users.route('/')
class UserCreateAndRead(Resource):
    @ns_users.doc(description="관리자가 모든 시스템 사용자를 조회할 때 사용됩니다.")
    @ns_users.marshal_list_with(user_model, code=200)
    @jwt_required()
    def get(self):
        '''모든 사용자 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")
        
        users = User.query.all()
        if not users:
            return {'message': '사용자가 존재하지 않습니다'}, 204
        
        return users
    
    @ns_users.doc(description="새로운 사용자를 생성합니다.")
    @ns_users.expect(register_model)
    @ns_users.marshal_with(user_model, code=201)
    @jwt_required()
    def post(self):
        '''신규 사용자 생성'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")

        data = request.json
        
        existing_user = User.query.filter_by(id=data['id']).first()
        if existing_user:
            abort(409, message="이미 존재하는 사용자 ID입니다.")
        
        new_user = User(
            id = data['id'],
            role=data['role'],
            name=data['name'],
            department=data['department'],
            admission_year=data['admission_year']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()

        return new_user, 201
    
# Update, Delete
@ns_users.route('/<id>')
@ns_users.param('id', '사용자 학번(직번)')
class UserUpdateAndDelete(Resource):
    @ns_users.doc(description="관리자가 특정 사용자 정보를 조회할 때 사용됩니다.")
    @ns_users.marshal_with(user_model)
    @jwt_required()
    def get(self, id):
        '''특정 사용자 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")

        user = User.query.get(id)
        if not user:
            abort(404, message="사용자를 찾을 수 없습니다.")

        return user

    @ns_users.doc(description="특정 사용자의 정보를 삭제합니다.")
    @jwt_required()
    def delete(self, id):
        '''특정 사용자 삭제'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")

        user = User.query.get(id)
        if not user:
            abort(404, message="사용자를 찾을 수 없습니다.")
        
        db.session.delete(user)
        db.session.commit()

        return "데이터를 삭제했습니다.", 204
    
    @ns_users.doc("")
    @ns_users.expect(register_model)
    @jwt_required()
    def put(self, id):
        '''특정 사용자 정보 수정'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")
        
        user = User.query.get(id)
        if not user:
            abort(404, message="사용자를 찾을 수 없습니다.")
        
        data = request.json

        if 'id' in data:
            user.id = data['id']
        if 'password' in data:
            user.set_password(data['password'])
        if 'name' in data:
            user.name = data['name']        
        if 'department' in data:
            user.department = data['department']
        if 'admission_year' in data:
            user.admission_year = data['admission_year']
        if 'role' in data:
            user.role = data['role']
        
        db.session.commit()

        response_data = {
            'id': user.id,
            'password': data['password'],
            'role': user.role,
            'name': user.name,
            'department': user.department,
            'admission_year': user.admission_year,
        }

        return response_data, 201
