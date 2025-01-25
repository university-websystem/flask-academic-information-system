from flask import request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Subject
from .. import db

# 과목 정보 CRUD
# 과목 관련 네임스페이스
ns_subjects = Namespace('subjects', description='과목 정보 CRUD')

# 과목 모델 정의
subject_model = ns_subjects.model('Subject', {
    'code': fields.String(required=True, description='과목 코드'),
    'name': fields.String(required=True, description='과목명'),
    'credits': fields.Integer(required=True, description='학점'),
    'professor_id': fields.String(description='교수 ID')
})

# Create, Read
@ns_subjects.route('/')
class SubjectCreateAndRead(Resource):
    @ns_subjects.doc(description="관리자가 모든 과목을 조회할 때 사용됩니다.")
    @ns_subjects.marshal_list_with(subject_model)
    @jwt_required()
    def get(self):
        '''모든 과목 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")
        
        subjects = Subject.query.all()
        return subjects

    @ns_subjects.doc(description="관리자가 새로운 과목을 추가할 때 사용됩니다.")
    @ns_subjects.expect(subject_model)
    @ns_subjects.marshal_with(subject_model, code=201)
    @jwt_required()
    def post(self):
        '''새로운 과목 추가'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")
        
        data = request.json
        subject = Subject(
            code=data['code'],
            name=data['name'],
            credits=data['credits'],
            professor_id=data.get('professor_id')
        )

        db.session.add(subject)
        db.session.commit()

        return subject, 201

# Update, Delete
@ns_subjects.route('/<subject_name>')
@ns_subjects.param('subject_name', '과목 이름')
class SubjectUpdateAndDelete(Resource):
    @ns_subjects.doc(description="관리자가 특정 과목을 조회할 때 사용됩니다.")
    @ns_subjects.marshal_with(subject_model)
    @jwt_required()
    def get(self, subject_name):
        '''특정 과목 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")

        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            abort(404, "과목을 찾을 수 없습니다.")

        return subject
    
    @ns_subjects.doc(desciption="관리자가 특정 과목을 삭제할 때 사용됩니다.")
    @jwt_required()
    def delete(self, subject_name):
        '''특정 과목 삭제'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")

        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            abort(404, message="과목을 찾을 수 없습니다.")

        db.session.delete(subject)
        db.session.commit()

        return "과목을 삭제했습니다.", 204
    
    @ns_subjects.doc(description="관리자가 특정 과목의 정보를 변경할 때 사용됩니다.")
    @ns_subjects.expect(subject_model)
    @ns_subjects.marshal_with(subject_model)
    @jwt_required()
    def put(self, subject_name):
        '''특정 과목 수정'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role != 'admin':
            abort(403, message="관리자만 접근 가능합니다.")
                  
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            abort(404, message="해당 과목을 찾을 수 없습니다.")

        data = request.json

        subject.code = data['code']
        subject.name = data['name']
        subject.credits = data['credits']
        subject.professor_id = data['professor_id']

        db.session.commit()

        return subject