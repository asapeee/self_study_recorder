import random
import cv2
import numpy as np
import torch
import torchvision
import os
import io
import base64
from io import BytesIO


from datetime import datetime

import uuid
from pathlib import Path

from apps.app import db
from apps.crud.models import Student, Administrator
from apps.recorder.models import StudentRecord, StudentMonthRecord
from apps.recorder.forms import MyPageForm, StartForm, FinishForm
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

import matplotlib.pyplot as plt
import numpy as np

def fig_to_base64_image(fig):
    io = BytesIO()
    fig.savefig(io, format="png")
    io.seek(0)
    base64_image = base64.b64encode(io.read()).decode()

    return base64_image

rc = Blueprint('recorder', __name__, template_folder='templates')


@rc.route('/', methods=['GET', 'POST'])
def index():
    month = str(datetime.now().month)
    year = str(datetime.now().year)
    year_month = year + '_' + month
    student_month_ranking = StudentMonthRecord.query.filter_by(year_month=year_month).order_by(StudentMonthRecord.total_time.desc()).limit(3).all()
    student_records = StudentRecord.query.filter(StudentRecord.finished_at==None).all()
    mypage_form = MyPageForm()
    if mypage_form.validate_on_submit():
        studentname_hiragana = mypage_form.studentname_hiragana.data
        student = Student.query.filter_by(studentname_hiragana=studentname_hiragana).first()
        if student is not None:
            return redirect(url_for('recorder.record', student_name=student.studentname))
        else:
            flash("その生徒はいません。")
    return render_template('recorder/index.html', mypage_form=mypage_form, month=month, student_month_ranking=student_month_ranking, student_records=student_records)


@rc.route('/record/<student_name>', methods=['GET', 'POST'])
def record(student_name):
    start_form = StartForm()
    finish_form = FinishForm()
    student = Student.query.filter_by(studentname=student_name).first()
    student_record = StudentRecord.query.order_by((StudentRecord.started_at.desc())).filter_by(student_id=student.id).first()
    date = datetime.now().date()
    student_day_records = StudentRecord.query.filter_by(student_id=student.id).filter(StudentRecord.started_at.like(f"%{date}%")).all()

    fig = plt.figure(figsize=(12, 4))
    x = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
    y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    year = datetime.now().year
    student_month_records = StudentMonthRecord.query.filter_by(student_id=student.id).filter(StudentMonthRecord.year_month.like(f"%{year}%")).all()

    # year_monthとxの月が一致するときにyにtotaltimeを代入
    for student_month_record in student_month_records:
        for idx, month in enumerate(x):
            if str(month) == student_month_record.year_month[-2:]:
                y[idx] = (student_month_record.total_time / 3600)
    plt.xticks(x, rotation=90)
    plt.bar(x, y)
    plt.title('月ごとの自習時間', fontname="MS Gothic")
    plt.xlabel('月', fontname="MS Gothic")
    plt.ylabel('自習時間 [時間]', fontname="MS Gothic")
    img = fig_to_base64_image(fig)
    return render_template('recorder/record.html', student=student, start_form=start_form, finish_form=finish_form, student_record=student_record, student_day_records=student_day_records, img=img)


@rc.route('/record/<student_name>/start', methods=['GET', 'POST'])
def start(student_name):
    student = Student.query.filter_by(studentname=student_name).first()
    student_record = StudentRecord(
        student_id=student.id,
        studentname=student.studentname,
        started_at=datetime.now().replace(microsecond=0)
    )

    year_month = str(datetime.now().year) + '_' + str(datetime.now().month)

    if StudentMonthRecord.query.filter_by(student_id=student.id, year_month=year_month).first() is None:
        student_month_record = StudentMonthRecord(
            student_id=student.id,
            studentname=student.studentname,
            year_month=year_month
        )
        db.session.add(student_month_record)
        db.session.commit()

    db.session.add(student_record)
    db.session.commit()

    return redirect(url_for('recorder.record', student_name=student_name))


@rc.route('/record/<student_name>/finish', methods=['GET', 'POST'])
def finish(student_name):
    student = Student.query.filter_by(studentname=student_name).first()
    student_record = StudentRecord.query.order_by((StudentRecord.started_at.desc())).filter_by(student_id=student.id).first()
    student_record.finished_at = datetime.now().replace(microsecond=0)
    study_time = student_record.finished_at - student_record.started_at
    student_record.study_time = study_time.seconds
    db.session.add(student_record)
    db.session.commit()
    
    year_month = str(datetime.now().year) + '_' + str(datetime.now().month)
    student_month_record = StudentMonthRecord.query.filter_by(student_id=student.id, year_month=year_month).first()

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
