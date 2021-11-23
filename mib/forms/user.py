import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, EmailField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email

from mib.validators.age import AgeValidator


class UserForm(FlaskForm):
    """
    Form created to allow the customers sign up to the application.
    This form requires all the personal information, in order to create the account.
    """    
    photo = f.FileField('Photo')
    email = f.StringField('Email', validators=[DataRequired()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    birthdate = f.DateField('Birthday', format='%d/%m/%Y')
    badwords = f.StringField('Badwords', widget = TextArea())
    #blacklist = f.StringField('Blacklist', widget = TextArea())
    display = ['photo', 'email', 'firstname', 'lastname', 
                'password', 'birthdate', 'badwords']

# Form created to report a user
class ReportForm(FlaskForm):
    email = f.StringField('Email', validators=[DataRequired()])
    reason = f.StringField('Reason', widget = TextArea())
    display = ['email','reason']