from flask import Blueprint, redirect, render_template
from flask.globals import request
from flask_login import current_user, login_required
import re
#from mib.database import User, db, Message, Messages
from mib.forms.message import MessageForm
from mib.rao.message_manager import MessageManager
from mib.rao.user_manager import UserManager
from mib.rao.message import Message
from datetime import datetime, time
from base64 import b64encode

message = Blueprint('message', __name__) 

# Messages on rendering (message and code)
CHANGE_BODY = 'Change body!'
USER_INEXISTENT = ' not registered'
BLACKLIST = " doesn't want messages from you"
FORBIDDEN_WORDS = 'Forbidden words for '
SCHEDULED = 'Scheduled!'
DATE_ERROR = 'Date format DD/MM/YYYY hh:mm'
DRAFT = 'Draft!'

# ------ ROUTES -------
@message.route('/mailbox/forward/<id>', methods=['POST', 'GET'])
def forward(id):
    """    
    Forward the message with id = id
    Renders a template to fill
    """
    message = MessageManager.get_message_by_id(id)
    if not message:
        return redirect('/mailbox')
    return edit_message('', message)


@message.route('/mailbox/reply/<id>', methods=['POST', 'GET'])
def reply(id):
    """    
    Reply to the message with id = id
    Renders a template to fill
    """
    message = MessageManager.get_message_by_id(id)
    if not message:
        return redirect('/mailbox')
    return edit_message(message.sender, None)


@message.route('/message/', defaults={'receiver': ''}, methods = ['GET', 'POST'])
@message.route('/message/<receiver>', methods = ['GET', 'POST'])
@login_required
def edit_message(receiver, msg = None):
    """
    Edit or create a new message, msg is None when the message is created,
    msg is not None when the message is draft
    Renders a template
    """
    form = MessageForm()
    # check if the requested message already exists
    if (msg != None and form.body.data == None):
        form = fill_message_form_from_message(msg)
    if request.method == 'GET':
        suggest = "README: separate each recipient with a ','"
        form.receiver.data = receiver
        return render_template("message.html",
            message = msg if msg else None,
            # pass the photo if it exists
            mphoto = 'data:image/jpeg;base64,' 
                + msg.photo if msg and msg.photo != '' else None, 
            form = form, suggest = suggest)
    else:
        # build the message
        message = build_message(form, msg)
        photo = 'data:image/jpeg;base64,' + message.photo if message.photo != '' else None
        if form.validate_on_submit():
            # checking if it is new (scheduled) or edited (draft)
            if form.choice.data == 'Schedule':
                # render a template with correct values
                # (message ok for every dest, massage ok for some dests, 
                # message not ok for anyone)
                code, data = validate_message(message)
                # user doesn't exists
                if (code == USER_INEXISTENT):
                    return render_template("message.html", 
                        mphoto = photo if msg else None,
                        message = message,
                        wrong_dest = data + USER_INEXISTENT, 
                        form = form)
                # current user is in the blacklist of the dest
                if (code == BLACKLIST):
                    return render_template("message.html", 
                        mphoto = photo if msg else None,
                        message = message,
                        blacklist_dest = data + BLACKLIST, 
                        form = form)
                # forbidden words for every dest
                if code == CHANGE_BODY:
                    return render_template("message.html", 
                        mphoto = photo if msg else None,
                        message = message,
                        error = CHANGE_BODY, 
                        form = form)
                # forbidden words for some dest
                if code == FORBIDDEN_WORDS:
                    return render_template("message.html", 
                        mphoto = photo if msg else None,
                        message = message,
                        forbidden = FORBIDDEN_WORDS +
                            data + '! The message has been scheduled removing them.', 
                        form = form)
                # message can be scheduled, remove msg from draft
                draft_remove(msg)
                if code == SCHEDULED:
                    return render_template("message.html", 
                        mphoto = photo,
                        message = message,
                        disabled = True, 
                        scheduled = SCHEDULED, 
                        form = form)
            # user wants to draft/edit a message 
            else:
                # Check if message already exists, it is to draft
                update_draft_message(message) if msg!= None else draft_new_message(message)  
                return render_template("message.html", 
                    mphoto = photo,
                    message = message,
                    disabled = True,
                    form = form, 
                    draft = DRAFT)
        # invalid date
        else:
            # photo = 'data:image/jpeg;base64,' + msg.photo if msg and msg.photo != '' else None,
            return render_template('message.html',
                mphoto = photo if msg else None,
                message = message,
                form = form, 
                date_error_message = DATE_ERROR)


# ----- HELPER FUNCTIONS ------ 

# Check if the message is valid to be sent
def validate_message(message):
    updated_list = []
    recipients = message.receiver
    # get the recipients list 
    recipients_list = recipients.split(", ")
    len_lis = len(recipients_list)
    # check if the recipients are registered
    not_registered = check_dests(recipients_list)
    if not_registered != "":
        return (USER_INEXISTENT, not_registered)
    """# check if the recipients are deleted (but still registered because they
    # don't have empty scheduled queue)
    deleted = check_deleted(recipients_list)
    if deleted != "":
        return (USER_INEXISTENT, deleted)"""
    # check if the sender is in one of the recipient's blacklist 
    blacklist = check_blacklist(recipients_list)
    if blacklist != "":
        return (BLACKLIST, blacklist)
    # check for each recipient if there is someone that doesn't accept one
    # of the words in the body
    removed_dst = ''
    for email in recipients_list:
        if check_words(message, email):
            print(email)
            if removed_dst == '':
                removed_dst = email
            else:
                removed_dst = removed_dst + ", " + email
        else:
            updated_list.append(email)
    return result_send(updated_list, len_lis, message, removed_dst)


def check_words(message, rec):
    """
    Check message body to avoid badwords for a particular receiver
    """
    receiver = UserManager.get_user_by_email(rec)
    badwords = UserManager.get_badwords_by_user_id(receiver.id)
    if badwords == []:
        return False
    # deletes comma, dot, etc..
    cleaned_body = re.split('\W', message.body)
    for word in badwords:
        if word in cleaned_body:
            print("c'è una parola")
            return True
    return False


# Check if all the recipients of the message are registered
def check_dests(recipients_list):
    unregistered = ""
    # contact user ms
    users = UserManager.get_all_users()
    # get a list of all registered users
    registered_users = [user.email for user in users]
    # for each recipient, check if it is in the list of registered user
    #return [user for user in recipients_list if user not in registered_users]
    for user in recipients_list:
        # if there is a not registered user, return its email
        if user not in registered_users:
            if unregistered == "":
                unregistered = unregistered + user
            else:
                unregistered = unregistered + ", " + user
    return unregistered

# Check if all the recepients are not deleted
def check_deleted(recipients_list):
    deleted = ""
    deleted_users = []
    users = UserManager.get_all_users()
    # get a list of all registered users
    for u in users:
        if (u.deleted == True):
            deleted_users.append(u.email)
    for item in recipients_list:
        if item in deleted_users:
            if deleted == "":
                deleted = deleted + item
            else:
                deleted = deleted + ", " + item
    return deleted

# Check if the sender is in one of the recipient's blacklist
def check_blacklist(recipients_list):
    blacklisted_by = ""
    # for each recipient get the black list and ensure the sender is not present
    for email in recipients_list:
        user = UserManager.get_user_by_email(email)
        blacklist = UserManager.get_blacklist_by_user_id(user.id)
        # if the sender is in the recipient "item" blacklist, return the recipient
        if current_user in blacklist:
            if blacklisted_by == "":
                blacklisted_by = blacklisted_by + email
            else:
                blacklisted_by = blacklisted_by + ", " + email
    return blacklisted_by


# Auxiliary fuction to check if the message can be sent 
# or there are some problems, content or recipients related
def result_send(updated_list, len_lis, message, removed_dst):
    # now the recipients list is updated
    # if there are no words forbidden for any recipient in the list
    # the message can be scheduled
    if len(updated_list) == len_lis:
        send_message(message)
        return (SCHEDULED, [])
    # else someone of the recipients has been removed
    else:
        # if the updated list is empty, the sender has to change the message body
        # because the message will not be sent to anyone
        if len(updated_list) == 0:
            return (CHANGE_BODY, [])
        # else, the recipients list is not empty, so the message will be sent 
        # to the recipients who accept the body of the message
        else:
            updated_dest = ''.join(updated_list)
            message.dest = updated_dest
            send_message(message)
            return (FORBIDDEN_WORDS, removed_dst)


# Draft a message when user tap the draft button for a new message
def draft_new_message(message):
    # save to db the last index
    MessageManager.create_message(message)

# Draft a message when user tap the save button
def update_draft_message(message):
    # get the draft messages of current user
    MessageManager.update_message(message)
"""    messages = Messages().to_messages(draft)
    # find the message with same id and swap it
    for msg in messages.messages:
        if msg.id == old.id:
            msg.dest = new.dest
            msg.body = new.body
            msg.time = new.time
            msg.photo = new.photo
            msg.bold = new.bold
            msg.italic = new.italic
            msg.underline = new.underline
            # msg.id = new.id
            # avoid pythest missing
            # break
    current_user.draft = messages.to_string()
    db.session.commit()"""


# Remove the draft from draft when it has been sent
def draft_remove(message: Message):
    if not message:
        return
    # get the draft messages of current user
    message.draft = False
    message.scheduled = True
    MessageManager.update_message(message)


def send_message(message: Message):
    """
    Send a message when user tap the save button
    """
    # iterate on string receiver
    receiver_emails = message.receiver.split(', ')
    for receiver_email in receiver_emails:
        message.receiver = receiver_email
        MessageManager.create_message(message)

# build a new message if msg is None, else edit msg 
# (build a new message with same id of msg)
def build_message(form, msg):
    # covert date to string
    str_date = date_to_string(form.date.data, form.time.data)
    # check if there is an image attached
    file = form.photo.data
    image_string = msg.photo if msg else ''
    if request.form.get('confirm') and request.form.get('confirm') == '0':
        image_string = ''
    elif request.form.get('confirm') and request.form.get('confirm') == '1':
        byte_image = b64encode(file.read())
        image_string = byte_image.decode('utf-8')
    # build the message to draft or to send

    #print(request.form.to_dict())
    message = Message()
    # fake id
    message.id = msg.id if msg else -1
    message.sender = current_user.email
    message.receiver = form.receiver.data
    message.body = form.body.data
    message.timestamp = str_date
    message.photo = image_string
    message.draft = True if request.form.get('choice') == 'Draft' else False
    message.scheduled = not message.draft
    #message.sent = 0
    #message.read = False
    message.bold = True if request.form.get('bold') else False
    message.italic = True if request.form.get('italic') else False
    message.underline = True if request.form.get('underline') else False
    return message


# Return the message with id 'id' 
def get_message_by_id(messages, id):
    m = None
    for message in messages:
        if (message.id == id):
            # avoid pytest missing
            m = message
    return m


# Programatically fill a message form
def fill_message_form_from_message(message):
    date = datetime.strptime(message.timestamp.split(' ')[0], '%d/%m/%Y')
    time = datetime.strptime(message.timestamp.split(' ')[1], '%H:%M')    
    form = MessageForm()
    form.receiver.data = message.receiver
    form.body.data = message.body
    form.date.data = date
    form.time.data = time
    form.choice.data = 'Schedule'
    return form

def date_explosion(message):  
    date = datetime.strptime(message.timestamp, '%Y-%m-%dT%H:%M:%SZ')
    date = date.strftime('%d/%m/%Y %H:%M')
    day = datetime.strptime(date.split(" ")[0], "%d/%m/%Y")
    time = datetime.strptime(date.split(" ")[1], '%H:%M')
    return day, time


# covert the date into a string
def date_to_string(date, time):
    try:
        str_date = date.strftime('%d/%m/%Y')
    except:
        str_date = ''
    try:
        str_time = time.strftime('%H:%M')
    except: 
        str_time = ''
    return str_date + ' ' + str_time        