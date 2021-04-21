from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, TextField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):
    content = TextField("Оставьте свой комментарий:", validators=[DataRequired()])
    submit = SubmitField('Отправить')