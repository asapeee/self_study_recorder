from flask import Blueprint, render_template, redirect, url_for, flash
from apps.app import db
from apps.crud.models import Student
from apps.crud.forms import StudentForm, DeleteStudentForm, DeleteStudentRecordForm, EditForm
from apps.recorder.models import StudentRecord, StudentMonthRecord
from flask_login import login_required

from datetime import datetime, timedelta
import pytz
crud = Blueprint(
    'crud',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@crud.route('/')
@login_required
def index():
    return render_template('crud/index.html')


@crud.route('/student/new', methods=['GET', 'POST'])
@login_required
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        studentname = form.studentname.data
        studentname = studentname + '　' * (15 - len(studentname))
        student = Student(
            studentname=studentname,
        )

        db.session.add(student)
        db.session.commit()

        return redirect(url_for('crud.students'))

    return render_template('crud/create.html', form=form)


@crud.route('/students')
@login_required
def students():
    students = Student.query.order_by(Student.studentname).all()
    return render_template('crud/index.html', students=students)


@crud.route('/students/<student_name>', methods=['GET', 'POST'])
@login_required
def check_student(student_name):
    delete_student_form = DeleteStudentForm()
    date = (datetime.utcnow() + timedelta(hours=9)).date()
    student = Student.query.filter_by(studentname=student_name).first()
    student_day_records = StudentRecord.query.filter_by(student_id=student.id).filter(date <= StudentRecord.started_at).filter(StudentRecord.started_at < date+timedelta(days=1)).all()
    student_records = StudentRecord.query.filter_by(student_id=student.id).order_by(StudentRecord.started_at.desc()).all()
    return render_template('crud/check.html', student=student, student_records=student_records, student_day_records=student_day_records, delete_student_form=delete_student_form)


@crud.route('/students/<student_name>/delete', methods=['POST'])
@login_required
def delete_student(student_name):
    student = Student.query.filter_by(studentname=student_name).first()
    student_records = StudentRecord.query.filter_by(student_id=student.id).all()
    for student_day_record in student_records:
        db.session.delete(student_day_record)
    student_month_records = StudentMonthRecord.query.filter_by(student_id=student.id).all()
    for student_month_record in student_month_records:
        db.session.delete(student_month_record)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('crud.students'))


@crud.route('/students/<student_name>/<student_records_id>', methods=['GET', 'POST'])
@login_required
def edit_student_record(student_name, student_records_id):
    student_record = StudentRecord.query.filter_by(studentname=student_name, id=student_records_id).first()

    edit_form = EditForm(student_record.started_at, student_record.finished_at)
    delete_student_record_form = DeleteStudentForm()

    if edit_form.validate_on_submit():
        student_record.started_at = edit_form.started_at.data
        student_record.finished_at = edit_form.finished_at.data

        if student_record.started_at < student_record.finished_at:
            student_record.study_time = (student_record.finished_at - student_record.started_at).seconds
            db.session.add(student_record)
            db.session.commit()

            year = (datetime.utcnow() + timedelta(hours=9)).year
            month = (datetime.utcnow() + timedelta(hours=9)).month
            str = f'{year}{month}01'
            dte = datetime.strptime(str, '%Y%m%d')
            if month == 12:
                next_str = f'{year+1}0101'
                next_dte = datetime.strptime(next_str, '%Y%m%d')
            else:
                next_str = f'{year}{month+1}01'
                next_dte = datetime.strptime(next_str, '%Y%m%d')
            student_records = StudentRecord.query.filter_by(studentname=student_name).filter(dte <= StudentRecord.started_at).filter(StudentRecord.started_at < next_dte).all()
            total_time = 0
            for student_record in student_records:
                total_time += student_record.study_time.seconds
            student_month_record = StudentMonthRecord.query.filter_by(studentneme=student_name, year=year, month=month).first()
            student_month_record.total_time = total_time
            db.session.add(student_month_record)
            db.session.commit()
            return redirect(url_for('crud.check_student', student_name=student_name))
        else:
            flash('自習時間が不適です．')
    return render_template('crud/edit.html', student_record=student_record, edit_form=edit_form, delete_student_record_form=delete_student_record_form)


@crud.route('/students/<student_name>/<student_records_id>/delete', methods=['POST'])
@login_required
def delete_student_record(student_name, student_records_id):
    print('--------------------------')
    student_record = StudentRecord.query.filter_by(studentname=student_name, id=student_records_id).first()
    if student_record:
        print('-------------------------------')
    db.session.delete(student_record)
    db.session.commit()
    return redirect(url_for('crud.check_student', student_name=student_name))

