import unittest
from flask import json
import os, sys

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# 관리자 권한 필요
class TestSubejctAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # 모든 과목 조회 
    def test_get_all_subjects(self):
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
        response = self.app.get('/subjects/', headers=headers)
        self.assertEqual(response.status_code, 200)

    # 과목 추가 후 삭제 성공 테스트
    def test_create_and_delete_subject_success(self):
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
        subject_data = {
            'code': 'CS101',
            'name': '컴퓨터과학개론',
            'credits': 3,
            'professor_id': 'P001'
        }
        create_response = self.app.post("/subjects/", data=json.dumps(subject_data), content_type='application/json', headers=headers)
        self.assertEqual(create_response.status_code, 201)
        data = json.loads(create_response.get_data(as_text=True))
        self.assertEqual(data['code'], 'CS101')
        self.assertEqual(data['name'], '컴퓨터과학개론')
        self.assertEqual(data['credits'], 3)
        self.assertEqual(data['professor_id'], 'P001')

        delete_response = self.app.delete(f"/subjects/{subject_data['name']}", headers=headers)
        self.assertEqual(delete_response.status_code, 204)

    # 특정 과목 조회 성공 테스트
    def test_get_subject_success(self):
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
        response = self.app.get('/subjects/C프로그래밍', headers=headers)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'C프로그래밍')
        self.assertEqual(data['code'], 'COMP101')
        self.assertEqual(data['credits'], 4)
        self.assertEqual(data['professor_id'], 'P001')

    # 특정 과목 조회 실패 테스트
    def test_get_subject_failure(self):
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
        response = self.app.get('/subjects/wrongSubjectName', headers=headers)
        self.assertEqual(response.status_code, 404)
        
if __name__ == '__main__':
    unittest.main()