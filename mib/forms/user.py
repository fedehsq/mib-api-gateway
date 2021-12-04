import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, EmailField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email
from wtforms.validators import Length

from mib.validators.age import AgeValidator


class UserForm(FlaskForm):
    """
    Form created to allow the customers sign up to the application.
    This form requires all the personal information, in order to create the account.
    """    
    photo = f.FileField('Photo')
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired(), Length(min = 5)])
    birthdate = f.DateField('Birthday', render_kw={"placeholder": "dd/mm/YYYY"}, format='%d/%m/%Y', validators = [AgeValidator(min_age = 18, max_age = 110)])
    points = f.StringField('Points')
    badwords = f.StringField('Badwords', widget = TextArea())
    blacklist = f.StringField('Blacklist', widget = TextArea(), default="")
    display = ['photo', 'email', 'firstname', 'lastname', 
                'password', 'birthdate', 'points', 'badwords', 'blacklist']

# Form created to report a user
class ReportForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    reason = f.StringField('Reason', widget = TextArea())
    display = ['email','reason']