from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import DataRequired, Email, length


class MyPageForm(FlaskForm):
    studentname_hiragana = StringField(
        '名前(ひらがな)',
        validators=[
            DataRequired(message='名前は必須です．'),
            length(max=30, message='30文字以内で入力してください．'),
        ],
    )

    submit = SubmitField('マイページへ')


class StartForm(FlaskForm):
    submit = SubmitField("自習開始")


class FinishForm(FlaskForm):
    submit = SubmitField("自習終了")
