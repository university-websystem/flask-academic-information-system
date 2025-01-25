from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()

authorizations = {
    'BearerAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': '''JWT 인증 헤더를 사용합니다.
        - JavaScript로 요청을 보낼 때는, 요청 헤더에 "Authorization: Bearer {token}"을 포함해야 합니다.
        - Swagger UI에서 테스트할 경우, "Authorize" 버튼을 클릭하고, "Value" 칸에 "Bearer {token}"을 입력하여 인증을 완료합니다.
        '''
    }
}

api = Api(
    version='1.0',
    title='학사 정보 시스템 API',
    description='학사 정보 관리 API',
    authorizations=authorizations,
    security='BearerAuth'
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    from .routes.auth import ns_auth
    from .routes.user import ns_users
    from .routes.subject import ns_subjects
    from .routes.grade import ns_grades

    api.add_namespace(ns_auth)
    api.add_namespace(ns_users)
    api.add_namespace(ns_subjects)
    api.add_namespace(ns_grades)

    with app.app_context():
        db.create_all()
    
    return app

