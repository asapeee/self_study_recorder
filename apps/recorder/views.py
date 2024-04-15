import base64
from io import BytesIO

from datetime import datetime, timedelta, time

import uuid
from pathlib import Path

from apps.app import db
from apps.crud.models import Student, Administrator
from apps.recorder.models import StudentRecord, StudentMonthRecord
from apps.recorder.forms import StartForm, FinishForm
from flask import (
    Blueprint,
    render_template,
    current_app,
    send_from_directory,
    redirect,
    url_for,
    flash,
    request,
)
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user, login_required
from apps.auth.forms import LoginForm
from flask_login import login_user, logout_user
import matplotlib.pyplot as plt
import pytz


def fig_to_base64_image(fig):
    io = BytesIO()
    fig.savefig(io, format="png")
    io.seek(0)
    base64_image = base64.b64encode(io.read()).decode()

    return base64_image


rc = Blueprint('recorder', __name__, template_folder='templates')


@rc.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        administrator = Administrator.query.filter_by(administratorname=form.administratorname.data).first()

        if administrator is not None and administrator.verify_password(form.password.data):
            login_user(administrator)
            return redirect(url_for('crud.students'))
        
        flash('管理者名かパスワードが不正です．')
    
    return render_template('recorder/login.html', form=form)


@rc.route('/', methods=['GET', 'POST'])
@login_required
def index():
    month = str((datetime.utcnow() + timedelta(hours=9)).month)
    year = str((datetime.utcnow() + timedelta(hours=9)).year)
    student_month_ranking = StudentMonthRecord.query.filter_by(year=year, month=month).order_by(StudentMonthRecord.total_time.desc()).limit(3).all()
    student_records = StudentRecord.query.filter(StudentRecord.finished_at==None).all()
    students_table = Student.query.order_by(Student.studentname).all()

    count_left = 0
    count_center = 0

    for i, student in enumerate(students_table):
        if student.studentname[0] < 'タ':
            count_left += 1
        elif 'タ' <= student.studentname[0] < 'マ':
            count_center += 1
    
    students_table_left = Student.query.order_by(Student.studentname).limit(count_left).all()
    students_table_center = Student.query.order_by(Student.studentname).limit(count_center).offset(count_left).all()
    students_table_right = Student.query.order_by(Student.studentname).offset(count_left + count_center).all()
    return render_template('recorder/index.html', month=month, student_month_ranking=student_month_ranking, student_records=student_records, students_table_left=students_table_left, students_table_center=students_table_center, students_table_right=students_table_right)


@rc.route('/<student_name>', methods=['GET', 'POST'])
@login_required
def record(student_name):
    start_form = StartForm()
    finish_form = FinishForm()
    student = Student.query.filter_by(studentname=student_name).first()
    student_record = StudentRecord.query.order_by((StudentRecord.started_at.desc())).filter_by(student_id=student.id).first()
    date = (datetime.utcnow() + timedelta(hours=9)).date()
    date = datetime.combine(date, time())
    student_day_records = StudentRecord.query.filter_by(student_id=student.id).filter(date <= StudentRecord.started_at).filter(StudentRecord.started_at < date+timedelta(days=1)).all()

    fig = plt.figure(figsize=(12, 4))
    x = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
    y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    year = (datetime.utcnow() + timedelta(hours=9)).year
    month = (datetime.utcnow() + timedelta(hours=9)).month
    student_month_records = StudentMonthRecord.query.filter_by(student_id=student.id, year=year, month=month).all()


    # year_monthとxの月が一致するときにyにtotaltimeを代入
    for student_month_record in student_month_records:
        for idx, month in enumerate(x):
            if month == student_month_record.month:
                y[idx] = (student_month_record.total_time / 3600)
    plt.xticks(x, rotation=90)
    plt.bar(x, y)
    plt.title('monthly study time')
    plt.xlabel('month')
    plt.ylabel('study time [h]')
    img = fig_to_base64_image(fig)
    return render_template('recorder/record.html', student=student, start_form=start_form, finish_form=finish_form, student_record=student_record, student_day_records=student_day_records, img=img)


@rc.route('/<student_name>/start', methods=['GET', 'POST'])
@login_required
def start(student_name):
    student = Student.query.filter_by(studentname=student_name).first()
    student_record = StudentRecord(
        student_id=student.id,
        studentname=student.studentname,
        started_at=(datetime.utcnow() + timedelta(hours=9)).replace(microsecond=0)
    )

    year = (datetime.utcnow() + timedelta(hours=9)).year
    month = (datetime.utcnow() + timedelta(hours=9)).month

    if StudentMonthRecord.query.filter_by(student_id=student.id, year=year, month=month).first() is None:
        student_month_record = StudentMonthRecord(
            student_id=student.id,
            studentname=student.studentname,
            year=year,
            month=month
        )
        db.session.add(student_month_record)
        db.session.commit()

    db.session.add(student_record)
    db.session.commit()

    return redirect(url_for('recorder.record', student_name=student_name))


@rc.route('/<student_name>/finish', methods=['GET', 'POST'])
@login_required
def finish(student_name):
    student = Student.query.filter_by(studentname=student_name).first()
    student_record = StudentRecord.query.order_by((StudentRecord.started_at.desc())).filter_by(student_id=student.id).first()
    student_record.finished_at = (datetime.utcnow() + timedelta(hours=9)).replace(microsecond=0)
    study_time = student_record.finished_at - student_record.started_at
    student_record.study_time = study_time.seconds
    db.session.add(student_record)
    db.session.commit()
    
    year = (datetime.utcnow() + timedelta(hours=9)).year
    month = (datetime.utcnow() + timedelta(hours=9)).month
    student_month_record = StudentMonthRecord.query.filter_by(student_id=student.id, year=year, month=month).first()

    if student_month_record is not None:
        student_month_record.total_time = student_month_record.total_time + study_time.seconds
        db.session.add(student_month_record)
        db.session.commit()
    return redirect(url_for('recorder.record', student_name=student_name))


@rc.errorhandler(404)
def page_not_found(e):
    return render_template('recoder/404.html'), 404


@rc.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
