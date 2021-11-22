from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required

home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
@login_required
def index():
    # calculate the number of notifications 
    # number of message received to read + number of message sent that have been read       

    # get the list of messages that has to be read
    """messages = db.session.query(Message).filter(Message.receiver == current_user.id).all()"""
    return render_template("index.html", number = 0)