import unittest
from flask import json
import os, sys

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# 학생별 성적 조회
class TestGradeAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # 학생별 전체 성적 조회 성공 테스트
    def test_get_student_grades_success(self):
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
        response = self.app.get('/grades/student/2020001', headers=headers)
        self.assertEqual(response.status_code, 200)
    
    # 학생별 전체 성적 조회 실패 테스트
    def test_get_student_grades_failure(self):
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
        response = self.app.get('/grades/student/19013139', headers=headers)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['message'], "데이터에 접근 권한이 없습니다.")

# 과목별, 학기별 성적 조회
class TestGradesByAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # 과목별 성적 조회 성공 테스트
    def tests_get_subject_grades_success(self):
        login_data = {
            'id': 'P001',
            'password': '1234', 
            'role': 'professor'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = self.app.get('/grades/subject/C프로그래밍', headers=headers)
        self.assertEqual(response.status_code, 200)

    # 과목별 성적 조회 실패 테스트
    def test_get_subject_grades_failure(self):
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
        response = self.app.get('/grades/subject/wrongSubjectName', headers=headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.get_data(as_text=True))

    # 학기별 성적 조회 성공 테스트
    def test_get_semester_grades_success(self):
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
        response = self.app.get('/grades/semester/2021-1', headers=headers)
        self.assertEqual(response.status_code, 200)
    
    # ** 학기별 성적 조회 실패 테스트 (성적 없음) **
    def test_get_semester_grades_not_found(self):
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
        response = self.app.get('/grades/semester/2025-1', headers=headers)
        self.assertEqual(response.status_code, 404)

# 성적 입력 테스트
class TestGradeCreateAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # 이미 입력된 성적으로 성적 입력 실패 테스트
    def test_add_grade_failure1(self):
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
        grade_data = {
            'student_id': '2020001',
            'subject_code': 'COMP101',
            'semester': '2020-1',
            'score': 3.0,
            'grade': 'B'
        }
        response = self.app.post('/grades/', data=json.dumps(grade_data), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 400)
    
    # 권한 없음으로 인한 성적 입력 실패 테스트
    def test_add_grade_failure2(self):
        login_data = {
            'id': 'P001', 
            'password': '1234', 
            'role': 'professor'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        grade_data = {
            'student_id': '2020001',
            'subject_code': 'ELEC101',
            'semester': '2020-1',
            'score': 4.5,
            'grade': 'A+'
        }
        response = self.app.post('/grades/', data=json.dumps(grade_data),
                                 content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 403)

# 성적 수정 테스트
class TestGradeUpdateAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    # 성적 수정 성공 테스트
    def test_update_grade_success(self):
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
        grade_data = {
            'score': 4, 
            'grade': 'A'
        }
        response = self.app.put('/grades/student/2020001/semester/2020-1/subject/COMP101', 
                                data=json.dumps(grade_data), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)

    # 성적 수정 실패 테스트 (권한 없음)
    def test_update_grade_failure(self):
        login_data = {
            'id': 'P001', 
            'password': '1234', 
            'role': 'professor'
        }
        login_response = self.app.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        access_token = json.loads(login_response.get_data(as_text=True))['access_token']

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        grade_data = {
            'score': 4, 
            'grade': 'A'
        }
        response = self.app.put('/grades/student/2020001/semester/2020-1/subject/ELEC101', 
                                data=json.dumps(grade_data), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()