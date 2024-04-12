from datetime import datetime

from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# 生徒
class Student(db.Model, UserMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    studentname = db.Column(db.String, index=True)
    student_records = db.relationship('StudentRecord', backref='student', order_by='desc(StudentRecord.id)')
    student_month_records = db.relationship('StudentMonthRecord', backref='student', order_by='desc(StudentMonthRecord.id)')


# アプリ管理者
class Administrator(db.Model, UserMixin):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, primary_key=True)
    administratorname = db.Column(db.String, index=True)
    password_hash = db.Column(db.String)

    @property
    def password(self):
        raise AttributeError('読み取り不可')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, passrowd(password))
    

    def is_duplicate_administratorname(self):
        return Administrator.query.filter_by(administratorname=self.administratorname).first() is not None


@login_manager.user_loader
def load_administrator(user_id):
    return Administrator.query.get(user_id)
