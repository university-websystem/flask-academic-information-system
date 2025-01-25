import unittest
from flask import json
import os, sys

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# 관리자 권한 필요
class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # 모든 사용자 조회
    def test_all_get_users(self):
        login_data = {
            'id': 'A001',
            'password': '1234',
            'role': 'admin'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = self.app.get('/users/', headers=headers)
        self.assertEqual(response.status_code, 200)

    # 모든 사용자 조회 실패 (권한 부족)
    def test_get_all_users_failure(self):
        login_data = {
            'id': '2020001',
            'password': '1234',
            'role': 'student'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = self.app.get('/users/', headers=headers)
        self.assertEqual(response.status_code, 403)

    # 특정 사용자 조회 성공
    def test_get_specific_user_success(self):
        login_data = {
            'id': 'A001',
            'password': '1234',
            'role': 'admin'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = self.app.get('/users/2020001', headers=headers)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], '2020001')
        self.assertEqual(data['role'], 'student')
        self.assertEqual(data['name'], '김학생')
        self.assertEqual(data['department'], '컴퓨터공학과')
        self.assertEqual(data['admission_year'], 2020)

    # 특정 사용자 조회 실패 (존재하지 않는 사용자)
    def test_get_specific_user_failure(self):
        login_data = {
            'id': 'A001',
            'password': '1234',
            'role': 'admin'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = self.app.get('/user/1234567', headers=headers)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()