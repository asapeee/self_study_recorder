from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import DataRequired, Email, length



class StartForm(FlaskForm):
    submit = SubmitField("自習開始")


class FinishForm(FlaskForm):
    submit = SubmitField("自習終了")
