import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms_components import DateRange, TimeRange

from wtforms.widgets import TextArea
from datetime import date, time, datetime

class MessageForm(FlaskForm):
    receiver = f.StringField('To', validators=[DataRequired()])
    body = f.StringField('Message', validators=[DataRequired()], widget=TextArea())
    photo = f.FileField('Photo', default=None)
    date  = f.DateField('Date', format='%d/%m/%Y',
        default = date.today(),
        validators=[DataRequired(), DateRange(min = date.today())])
    time  = f.TimeField('Time', format='%H:%M',
        default = time(datetime.now().hour, datetime.now().minute),
        validators=[DataRequired()])
    choice = f.RadioField('Label', choices = [('Draft', 'Draft'),('Schedule', 'Schedule')], default='Schedule')
    display = ['receiver', 'body', 'photo', 'date', 'time' 'choice']

class ReadMessageForm(FlaskForm):
    sender = f.StringField('From')
    body = f.StringField('Message', widget = TextArea())
    date  = f.StringField('Date')
    display = ['from', 'body', 'date']

class ViewMessageForm(FlaskForm):
    receiver = f.Label('To', 'To')
    body = f.Label('Message', 'Message')
    date  = f.Label('Date', 'Message')
    display = ['receiver', 'body', 'date']