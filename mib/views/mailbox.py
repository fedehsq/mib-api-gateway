from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import login_required, current_user
from mib.rao.message_manager import MessageManager
from base64 import b64encode
from datetime import datetime

mailbox = Blueprint('mailbox', __name__)

# List all users to choose a recipient for a message
@mailbox.route('/mailbox')
@login_required
def show_mailbox():
    response = MessageManager.get_mailbox()
    return response
