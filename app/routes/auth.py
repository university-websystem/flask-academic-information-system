from flask import request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
from ..models import User

# 인증 네임스페이스
ns_auth = Namespace('auth', description='사용자 인증 관련 작업')

# 사용자 모델
user_model = ns_auth.model('User', {
    'id': fields.String(required=True, description='학번(직번)'),
    'role': fields.String(required=True, description='역할'),
    'name': fields.String(required=True, description='이름'),
    'department': fields.String(description='학과'),
    'admission_year': fields.Integer(required=True, description='입학년도(고용년도)')
})

# 로그인 요청 모델델
login_request = ns_auth.model('Login_Request', {
    'id': fields.String(required=True, description='학번(직번)'),
    'password': fields.String(required=True, description='비밀번호'),
    'role': fields.String(required=True, description='역할')
})

# 로그인 응답 모델델
login_response = ns_auth.model('Login_Response', {
    'access_token': fields.String(required=True, description='Access token for user'),
    'refresh_token': fields.String(required=True, description='Refresh token for user'),
    'user': fields.Nested(user_model)  
})

# 로그인 API
@ns_auth.route('/login')
class UserLogin(Resource):
    @ns_auth.doc(description="사용자 로그인 API. 로그인 시 아이디, 비밀번호, 역할을 확인합니다.")
    @ns_auth.expect(login_request)
    @ns_auth.marshal_with(login_response, code=200)
    def post(self):
        '''사용자 로그인'''
        data = request.json
        user = User.query.filter_by(id=data['id']).first()

        if not user:
            abort(401, message="아이디가 존재하지 않습니다.")

        if not user.check_password(data['password']):
            abort(401, message="비밀번호가 올바르지 않습니다.")

        if user.role != data['role']:
            abort(401, message="구분이 일치하지 않습니다.")

        identity = f"{user.id}:{user.role}"
        access_token = create_access_token(identity=identity, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(identity=identity, expires_delta=timedelta(days=30))
        return {
                'access_token' : access_token,
                'refresh_token' : refresh_token,
                'user' : {
                    'id' : user.id,
                    'role' : user.role,
                    'name' : user.name,
                    'department' : user.department,
                    'admission_year' : user.admission_year
                }
            }, 200
    
# 토큰 갱신 API
@ns_auth.route('/refresh')
class TokenRefresh(Resource):
    @ns_auth.doc(description='access token 만료 시 refresh token이 존재하면 재발급합니다.')
    @jwt_required(refresh=True)
    def post(self):
        '''엑세스 토큰 갱신'''
        current_user = get_jwt_identity()
        user_id, role = current_user.split(':')
        new_identity = f"{user_id}:{role}"
        access_token = create_access_token(identity=new_identity, expires_delta=timedelta(minutes=15))

        return {
            "access_token": access_token
        }