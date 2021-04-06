from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class SubscribeForm(FlaskForm):
    submit = SubmitField('Подписаться')