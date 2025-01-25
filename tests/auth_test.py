import unittest
from flask import json
import os, sys

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# 로그인 테스트
class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True
    
    # Login 성공
    def test_login_success(self):
        login_data = {
            'id': '2020001',
            'password': '1234',
            'role': 'student'
        }
        response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['id'], '2020001')
        self.assertEqual(data['user']['role'], 'student')

    # Login 실패
    def test_login_failure(self):
        login_data = {
            'id': '2020001', 
            'password': 'wrongpassword',  
            'role': 'student'
        }
        response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['message'], '비밀번호가 올바르지 않습니다.')

# 토큰 재발급 테스트
class TestTokenRefreshAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # Token 재발급 성공
    def test_access_token_refresh_success(self):
        login_data = {
            'id': '2020001',
            'password': '1234',
            'role': 'student'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        refresh_token = json.loads(login_response.get_data(as_text=True))['refresh_token']

        headers = {
            'Authorization': f'Bearer {refresh_token}'
        }
        response = self.app.post('/auth/refresh', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('access_token', data)

    # Token 재발급 실패
    def test_access_toekn_failure(self):
        response = self.app.post('/auth/refresh')
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()