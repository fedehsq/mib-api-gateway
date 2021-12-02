from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required
from mib.rao.message_manager import MessageManager


home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
@login_required
def index():
    # calculate the number of notifications 
    # number of message received to read + number of message sent that have been read       
    notifications = MessageManager.get_notifications_number(
        current_user.email, current_user.id)
    inbox = notifications['inbox']
    sent = notifications['sent']
    # get the list of messages that has to be read
    return render_template("index.html", number = inbox + sent)