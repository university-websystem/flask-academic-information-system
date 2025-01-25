from . import db
import hashlib

# 데이터베이스 users 테이블
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(10), primary_key=True) 
    role = db.Column(db.Enum('student', 'professor', 'admin', name='role_enum'), nullable=False) 
    name = db.Column(db.String(50), nullable=False) 
    department = db.Column(db.String(50)) 
    admission_year = db.Column(db.Integer, nullable=False) 
    password_hash = db.Column(db.String(255), nullable=False)

    subjects = db.relationship('Subject', backref='professor', lazy=True)
    grades = db.relationship('Grade', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

# 데이터베이스 subjects 테이블
class Subject(db.Model):
    __tablename__ = 'subjects'
    code = db.Column(db.String(10), primary_key=True) 
    name = db.Column(db.String(100), nullable=False) 
    credits = db.Column(db.Integer, nullable=False) 
    professor_id = db.Column(db.String(10), db.ForeignKey('users.id')) 

    grades = db.relationship('Grade', backref='subject', lazy=True)
    
# 데이터베이스 grades 테이블
class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    student_id = db.Column(db.String(10), db.ForeignKey('users.id')) 
    subject_code = db.Column(db.String(10), db.ForeignKey('subjects.code')) 
    semester = db.Column(db.String(6)) 
    score = db.Column(db.Float) 
    grade = db.Column(db.String(2)) 

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_code': self.subject_code,
            'semester': self.semester,
            'score': self.score,
            'grade': self.grade
        }