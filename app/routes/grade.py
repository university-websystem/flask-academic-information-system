from flask import request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Subject, Grade
from .. import db

# 성적 관련 네임스페이스
ns_grades = Namespace('grades', description='성적 입력, 수정, 조회')

# 성적 모델 정의
grade_model = ns_grades.model('Grade', {
    'id': fields.Integer(readOnly=True, description='성적 ID'),
    'student_id': fields.String(required=True, description='학생 ID'),
    'subject_code': fields.String(required=True, description='과목 코드'),
    'subject_name': fields.String(required=True, description='과목명'),
    'semester': fields.String(required=True, description='학기'),
    'score': fields.Float(required=True, description='성적 점수'),
    'grade': fields.String(required=True, description='성적 학점')
})

# 학생별 전체 성적 조회
@ns_grades.route('/student/<student_id>')
@ns_grades.param('student_id', '학번')
class GradesByStudent(Resource):
    @ns_grades.doc(description="학생이 자신의 성적을 조회할 시, 관리자나 교수가 특정 학생의 성적을 조회할 시 사용됩니다.")
    @ns_grades.marshal_list_with(grade_model)
    @jwt_required()
    def get(self, student_id):
        '''특정 학생의 성적 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role == 'student' and user_id != student_id:
            abort(403, message="데이터에 접근 권한이 없습니다.")

        grades = Grade.query.filter_by(student_id=student_id).all()
        if not grades:
            abort(404, message="학생의 성적을 찾을 수 없습니다.")

        grade_data = []
        for grade in grades:
            subject = Subject.query.filter_by(code=grade.subject_code).first()
            grade_data.append({
                'id': grade.id,
                'student_id': grade.student_id,
                'subject_code': grade.subject_code,
                'subject_name': subject.name if subject else '과목 이름 없음',  
                'semester': grade.semester,
                'score': grade.score,
                'grade': grade.grade
            })

        return grade_data, 200

# 과목별 성적 조회
@ns_grades.route('/subject/<subject_name>')
@ns_grades.param('subject_name', '과목 이름')
class GradesBySubject(Resource):
    @ns_grades.doc(description="학생이 자신이 수강한 특정 과목의 성적을 조회할 시, 교수가 자신이 담담하는 과목의 성적을 조회할 시, 관리자가 특정과목의 성적을 모두 조회할 시 사용됩니다.")
    @ns_grades.marshal_list_with(grade_model)
    @jwt_required()
    def get(self, subject_name):
        '''특정 과목의 성적 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            abort(404, message="해당 과목을 찾을 수 없습니다.")
        
        if role == "student":
            grades = Grade.query.filter_by(subject_code=subject.code, student_id=user_id).all()
            if not grades:
                abort(404, message="해당 과목의 성적이 없습니다.")

        elif role == "professor":
            if subject.professor_id != user_id:
                abort(403, message="담당하지 않은 과목의 성적은 조회할 수 없습니다.")
            grades = Grade.query.filter_by(subject_code=subject.code).all()
            if not grades:
                abort(404, message="해당 과목의 성적이 없습니다.")

        elif role == "admin":
            grades = Grade.query.filter_by(subject_code=subject.code).all()
            if not grades:
                abort(404, message="해당 과목의 성적이 없습니다.")
        
        else:
            abort(403, message="접근 권한이 없습니다.")
        
        grade_data = []
        for grade in grades:
            grade_data.append({
                'id': grade.id,
                'student_id': grade.student_id,
                'subject_code': grade.subject_code,
                'subject_name': subject.name,
                'semester': grade.semester,
                'score': grade.score,
                'grade': grade.grade
            })

        return grade_data, 200
    
# 학기별 성적 조회
@ns_grades.route('/semester/<semester>')
@ns_grades.param('semester', '학기')
class GradesBySemester(Resource):
    @ns_grades.doc(description="학생이 특정 학기에서 자신이 수강한 성적을 조회할 시, 교수가 특정 학기에서 자신이 담당한 과목의 성적을 조회할 시, 관리자가 특정 학기의 성적을 모두 조회할 시 사용됩니다.")
    @jwt_required()
    def get(self, semester):
        '''특정 학기의 성적 조회'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role == "student":
            grades = db.session.query(Grade, User.name).join(User, Grade.student_id == User.id)\
                      .filter(Grade.student_id == user_id, Grade.semester == semester).all()
            if not grades:
                abort(404, message=f"{semester} 학기에 해당하는 성적이 없습니다.")

        elif role == "professor":
            subjects = Subject.query.filter_by(professor_id=user_id).all()
            subject_codes = [subject.code for subject in subjects]
            grades = db.session.query(Grade, User.name).join(User, Grade.student_id == User.id)\
                        .filter(Grade.subject_code.in_(subject_codes), Grade.semester == semester)
            if not grades:
                abort(404, message="해당 학기에 담당하는 과목의 성적이 없습니다.")    
        
        elif role == "admin":
            grades = db.session.query(Grade, User.name).join(User, Grade.student_id == User.id)\
                      .filter(Grade.semester == semester).all()
            if not grades:
                abort(404, message="해당 학기에 담당한 성적이 없습니다.")
        else:
            abort(403, message="접근 권한이 없습니다.")

        grade_data = []
        for grade, student_name in grades:
            grade_data.append({
                'id': grade.id,
                'student_id': grade.student_id,
                'student_name': student_name,
                'subject_code': grade.subject_code,
                'subject_name': grade.subject.name,
                'semester': grade.semester,
                'score': grade.score,
                'grade': grade.grade
            })

        return grade_data, 200

# 성적 입력
@ns_grades.route('/')
class GradeInput(Resource):
    @ns_grades.doc(description="교수가 담당 과목에서 성적을 추가할 시, 관리자가 모든 과목에 성적을 추가할 시 사용됩니다.")
    @ns_grades.expect(grade_model)
    @jwt_required()
    def post(self):
        '''성적 입력 (교수: 담당 과목만, 관리자: 모든 과목)'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')
        
        if role not in ['professor', 'admin']:
            abort(403, message="접근 권한이 없습니다.")
        
        data = request.json
        subject = Subject.query.filter_by(code=data['subject_code']).first()

        if not subject:
            abort(404, message="해당 과목을 찾을 수 없습니다.")
        
        if role == "professor" and subject.professor_id != user_id:
            abort(403, message="담당하지 않은 과목에 성적을 입력할 수 없습니다.")
        
        existing_grade = Grade.query.filter_by(
            student_id=data['student_id'],
            subject_code=data['subject_code'],
            semester=data['semester']
        ).first()
        if existing_grade:
            abort(400, message='해당 과목의 성적이 이미 존재합니다.')
        
        grade = Grade(
            student_id=data['student_id'],
            subject_code=data['subject_code'],
            semester=data['semester'],
            score=data['score'],
            grade=data['grade']
        )

        db.session.add(grade)
        db.session.commit()

        return grade.to_dict(), 201

# 성적 수정
# 성적 수정 모델 정의
grade_input_model = ns_grades.model('GradeInput', {
    'score': fields.Float(required=True, description='성적 점수'),
    'grade': fields.String(required=True, description='성적 학점')
})

@ns_grades.route('/student/<string:student_id>/semester/<string:semester>/subject/<string:subject_code>')
@ns_grades.param('student_id', '학생 ID')
@ns_grades.param('semester', '학기')
@ns_grades.param('subject_code', '과목 코드')
class GradeResource(Resource):
    @ns_grades.doc(description="교수가 담당 과목의 성적을 수정할 시, 관리자가 모든 과목의 성적을 수정할 시 사용됩니다.")
    @ns_grades.expect(grade_input_model)
    @ns_grades.marshal_with(grade_model, code=200)
    @jwt_required()
    def put(self, student_id, semester, subject_code):
        """성적 수정 (교수: 담당 과목만, 관리자: 모든 과목)"""
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')

        if role not in ['professor', 'admin']:
            abort(403, message="접근 권한이 없습니다.")

        grade = Grade.query.filter_by(student_id=student_id, semester=semester, subject_code=subject_code).first()
        if not grade:
            abort(404, message="해당 성적 정보를 찾을 수 없습니다.")

        subject = Subject.query.filter_by(code=subject_code).first()
        if role == 'professor' and subject.professor_id != user_id:
            abort(403, message="담당하지 않은 과목의 성적을 수정할 수 없습니다.")

        data = request.json
        grade.score = data.get('score', grade.score)
        grade.grade = data.get('grade', grade.grade)

        db.session.commit()
        return {
            'id': grade.id,
            'student_id': grade.student_id,
            'subject_code': grade.subject_code,
            'subject_name' : grade.subject.name,
            'semester': grade.semester,
            'score': grade.score,
            'grade': grade.grade
        }, 200