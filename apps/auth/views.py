from flask import Blueprint, render_template, flash, url_for, redirect, request
from apps.app import db
from apps.auth.forms import SignUpForm, LoginForm
from apps.crud.models import Student, Administrator
from flask_login import login_user, logout_user


auth = Blueprint(
    'auth',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@auth.route('/')
def index():
    return render_template('auth/index.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        administrator = Administrator(
            administratorname=form.administratorname.data,
            password=form.password.data,
        )
        
        db.session.add(administrator)
        db.session.commit()
        login_user(administrator)
        next_ = request.args.get('next')
        if next_ is None or not next_.startswith('/'):
            next_ = url_for('auth.index')
        return redirect(next_)
    
    return render_template('auth/signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        administrator = Administrator.query.filter_by(administratorname=form.administratorname.data).first()

        if administrator is not None and administrator.verify_password(form.password.data):
            login_user(administrator)
            return redirect(url_for('recorder.index'))
        
        flash('管理者名かパスワードが不正です．')
    
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))