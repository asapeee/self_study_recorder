from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(FlaskForm):
    administratorname = StringField(
        '管理者名',
        validators=[
            DataRequired('管理者名は必須です．'),
            Length(1, 30, '30文字以内で入力してください．'),
        ],
    )

    password = PasswordField(
        'パスワード',
        validators=[DataRequired('パスワードは必須です．')]
    )

    submit = SubmitField('新規登録')


class LoginForm(FlaskForm):
    administratorname = StringField(
        '管理者名',
        validators=[
            DataRequired('管理者名は必須です．'),
            Length(1, 30, '30文字以内で入力してください．'),
        ],
    )
    
    password = PasswordField(
        'パスワード',
        validators=[DataRequired('パスワードは必須です．')]
    )

    submit = SubmitField('ログイン')

