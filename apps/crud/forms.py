from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, length


class StudentForm(FlaskForm):
    studentname = StringField(
        '生徒名(カタカナ)',
        validators=[
            DataRequired(message='生徒名(カタカナ)は必須です．'),
            length(max=30, message='30文字以内で入力してください．'),
        ],
        
    )


    submit = SubmitField('新規登録')


class DeleteStudentForm(FlaskForm):
    submit = SubmitField("生徒削除")


class DeleteStudentRecordForm(FlaskForm):
    submit = SubmitField("自習時間削除")


def EditForm(start, finish):
    class EditForm(FlaskForm):
        started_at = DateTimeField(
            '自習開始時間',
            default=start
        )

        finished_at = DateTimeField(
            '自習終了時間',
            default=finish
        )

        submit = SubmitField('修正')
    return EditForm()
