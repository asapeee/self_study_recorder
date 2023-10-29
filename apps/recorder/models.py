from datetime import datetime

from apps.app import db


class StudentRecord(db.Model):
    __tablename__ = 'student_records'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String, db.ForeignKey('students.id'))
    studentname = db.Column(db.String)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    study_time = db.Column(db.Float, default=0)


class StudentMonthRecord(db.Model):
    __tablename__ = 'student_month_records'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String, db.ForeignKey('students.id'))
    studentname = db.Column(db.String)
    year_month = db.Column(db.String)
    total_time = db.Column(db.Float, default=0)
