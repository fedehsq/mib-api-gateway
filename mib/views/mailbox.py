from os import times
from flask import Blueprint, redirect, render_template, request
from flask_login import login_required, current_user
from mib.rao.message_manager import MessageManager
from datetime import datetime, time
from mib.views.message import edit_message, fill_message_form_from_message

mailbox = Blueprint('mailbox', __name__)

# ------- ROUTES -------
@mailbox.route('/mailbox')
@login_required
def show_mailbox():
    """
    Renders a template showing the mailbox of the user
    """

    # fields filled if user is searching
    msg_field = request.args.get('msg')
    msg_user = request.args.get('user')
    msg_date = request.args.get('date')
    # get the number of new messages to display the notifications
    notifications = MessageManager.get_notifications_number(current_user.email)
    inbox = notifications['inbox']
    sent = notifications['sent']
    # no search request
    if not msg_field and not msg_user and not msg_date:
        return render_template("mailbox.html", inbox = inbox, sent = sent)
    # search request
    res_received, res_sent, res_to_be_sent = MessageManager.get_filtered_messages(
        current_user.email, msg_field, msg_user, msg_date)
    return render_template("mailbox/searched_list.html", 
        page_title = 'Search', 
        inbox = res_received,
        sent = res_sent,
        scheduled = res_to_be_sent,
       #read = read
    )

@mailbox.route('/mailbox/draft/', defaults={'id': ''}, methods = ['GET', 'POST'])
@mailbox.route('/mailbox/draft/<id>', methods=['GET', 'POST'])
@login_required
def draft(id):
    """
    Renders a template with the draft messages
    """
    # check if user wants to delete message
    check_delete_message()

    # check if the request is to see all messages...
    if (id == ''):
        draft = MessageManager.get_draft(current_user.email)
        return render_template("mailbox/messages_list_.html", 
        page_title = 'Draft', 
        messages = draft)
    # ... or if a fixed message is selected by id
    message = MessageManager.get_message_by_id(id)
    # launch template to edit if m is already in draft
    return edit_message(message.receiver, message) if message else redirect('/mailbox')


@mailbox.route('/mailbox/sent/', defaults={'id': ''}, methods = ['GET', 'POST'])
@mailbox.route('/mailbox/sent/<id>', methods=['GET', 'POST']) 
@login_required
# Show the sent messages or a message corresponding to a specific id
def sent(id):
    """
    Renders a template with the sent messages
    """
    check_delete_message()
    # check if the request is to see all messages...
    if (id == ''):
        # get the sent messages
        sent = MessageManager.get_sent(current_user.email)
        # get the read message by the receiver to display the notifications
        read_by_receiver = []
        for message in sent:
            if message.read == True and message.sent == 1:
                # to avoid display again the notification
                message.sent = 2
                read_by_receiver.append(message)
                MessageManager.update_message(message)
        return render_template("mailbox/messages_list_.html", 
            page_title = 'Sent', 
            messages = sent,
            read_msg = read_by_receiver) 
    # ... or if a fixed message is selected by id
    return render_message_by_id(id)
    

@mailbox.route('/mailbox/scheduled/', defaults={'id': ''}, methods = ['GET', 'POST'])
@mailbox.route('/mailbox/scheduled/<id>', methods=['GET', 'POST'])
@login_required
def scheduled(id):
    """
    Show the scheduled messages or a message corresponding to a specific id
    """
    # check if user wants to delete message and check if the user has points to do this
    #if (request.form.__contains__('delete') and current_user.points >= 150):
    check_delete_message()

        #current_user.points -= 150
    # check if the request is to see all messages...
    if (id == ''):
        scheduled = MessageManager.get_scheduled(current_user.email)
        return render_template("mailbox/messages_list_.html", 
            page_title = 'Scheduled', 
            messages = scheduled) 
            #points = current_user.points) 
    # ... or if a fixed message is selected by id
    return render_message_by_id(id) 


@mailbox.route('/mailbox/inbox/', defaults={'id': ''}, methods = ['GET', 'POST'])
@mailbox.route('/mailbox/inbox/<id>', methods=['GET', 'POST'])
@login_required
def inbox(id):
    """
    Show the inbox messages or the message corresponding to a specific id
    """
    # check if user wants to delete message
    check_delete_message()
    # check if the request is to see all messages...
    if (id == ''):
        # contacts the messages ms
        inbox = MessageManager.get_inbox(current_user.email)
        return render_template("mailbox/messages_list_.html", 
            page_title = 'Inbox', 
            messages = inbox) 
    # ... or if a fixed message is selected by id
    message = MessageManager.get_message_by_id(id)
    if not message:
        return redirect('/mailbox')
    # set the flag read to True, because the user is reading the message
    message.read = True
    MessageManager.update_message(message)
    # launch template to read the sent message
    form = fill_message_form_from_message(message)
    form.receiver.label = 'From'
    return render_template("message.html", 
        mphoto = 'data:image/jpeg;base64,' + message.photo if message.photo != '' else None,
        message = message,
        disabled = True, 
        form = form)

# ------- AUXILIARY FUNCTIONS -------
"""def search_messages(body, sender, date):
    Given the body (and/or) the sender (and/or) the date, 
    returns the filtered messages
    if not body and not sender and not date:
        return 0, 0, 0
    if date:
        try:
            msg_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            return "error"

    scheduled = MessageManager.get_scheduled(current_user.email)
    inbox = MessageManager.get_inbox(current_user.email)
    sent = MessageManager.get_sent(current_user.email)
    return filter_list(inbox, body, sender, msg_date),\
           filter_list(sent, body, sender, msg_date),\
           filter_list(scheduled, body, sender, msg_date)

def filter_list(messages, body, sender, date):
    Returns a filtered list 
    for m in messages:
        if body in m.body and sender in m.sender and date in m.timestamp:
            messages.append(m)"""


def check_delete_message():
    """
    Check if user wants to delete a message, 
    if so, contacts the messages ms
    """
    if (request.form.__contains__('delete')):
        message_id = request.form['delete']
        MessageManager.delete_message_by_id(message_id)

def render_message_by_id(id):
    """
    Renders template for the message with id = id
    """
    message = MessageManager.get_message_by_id(id)
    if not message:
        return redirect('/mailbox')
    # launch template to read the sent message
    form = fill_message_form_from_message(message)
    return render_template("message.html", 
        message = message,
        disabled = True,
        mphoto = 'data:image/jpeg;base64,' + message.photo if message.photo != '' else None,
        form = form)
"""
def render(message):
    # launch template to read the sent message
    form = fill_message_form_from_message(message)
    form.receiver.label = 'From'
    return render_template("message.html", 
        mphoto = 'data:image/jpeg;base64,' + message.photo if message.photo != '' else None,
        message = message,
        disabled = True, 
        form = form)"""
