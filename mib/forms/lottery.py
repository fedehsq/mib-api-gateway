import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange

class LotteryForm(FlaskForm):
    number = f.IntegerField('number', validators=[DataRequired(), NumberRange(min = 0, max = 100)])
    display = ['number']