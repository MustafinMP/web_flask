from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, TextField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):
    # title = StringField('Заголовок', validators=[DataRequired()])
    content = TextField("Оставьте свой комментарий:")
    submit = SubmitField('Отправить')