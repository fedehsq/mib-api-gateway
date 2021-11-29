import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

class LotteryForm(FlaskForm):
    number = f.IntegerField('number', validators=[DataRequired()])
    display = ['number']