from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_wtf.form import FlaskForm
from flask_login import login_required, current_user
from mib.forms.user import UserForm, ReportForm
from mib.rao.user_manager import UserManager
from mib.auth.user import DEFAULT_PIC, User
from base64 import b64encode
from datetime import datetime

users = Blueprint('users', __name__)

# -------- ROUTES --------

# Return filtered users
# List all searched users by name, surname or email
def search_users(searched_input):
    response = UserManager.search_users(searched_input)
    return response

# List all users to choose a recipient for a message
@users.route('/users', methods = ['GET'])
@login_required
def get_users():
    """
    Returns:
        All users registered to service.
    """
    response = UserManager.get_all_users()
    searched_input = request.args.get("search")
    if searched_input:
        # filter and show the list
        users = search_users(searched_input)
        return render_template("users.html", users = users, 
                               current_user = current_user, 
                               searched_input = "You searched: " + searched_input)
    else:
        # get all users list
        return render_template("users.html", users = response, 
                               current_user = current_user)

# Report a user
@users.route("/users/report/<email>", methods = ['GET','POST'])
@login_required
def report(email):
    form = ReportForm()
    if request.method == 'GET':
        form.email.data = email
        # get the form to report a user
        return render_template('report.html', form = form)
    else:
        if form.validate_on_submit():
            email = form.data["email"]
            code = UserManager.report(email)
            # check if the user exists, if not redirect to report page again
            if code == 404:
                return render_template('report.html', 
                    form = form, 
                    email_error_message = 'No user with this email.')
            else:
                return redirect("/")

@users.route('/register', methods=['GET', 'POST'])
def create_user():
    """
    This method allows the creation of a new user into the database
    Returns:
        Redirects the user into his profile page, once he's logged in
    """
    # check if the user is already logged, 
    # if so the user will be redirected to his dashboard
    if current_user.is_authenticated:
        return redirect("/")
    form = UserForm()
    # registration post request
    if request.method == 'POST':
        return user_registration(form)       
    else:
        # get the page
        suggest = "README: separate each forbidden word with a ',' "
        return render_template('register.html', mphoto = DEFAULT_PIC, form = form, suggest = suggest)


@users.route('/profile', methods=['POST', 'GET'])
@login_required
def get_profile():
    """
    Return:
        Get the profile information of the authenticated user
    """
    # request to open profile page
    if request.method == 'GET':
        return show_profile()
    else:
        # request to edit profile
        return edit_profile()

# -------- FUNCTIONS -------
def get_form_fields(form):
    """
    :param form: User Form
    Return:
        all values of the form.
    """
    return (
        form.data['email'],
        form.data['password'],
        form.data['firstname'],
        form.data['lastname'],
        form.data['birthdate'],
        'data:image/jpeg;base64,' + \
            b64encode(form.data['photo'].read()).decode('utf-8')
            if form.data['photo'] else DEFAULT_PIC,
        form.data['badwords'],
        form.data['blacklist']
    )


def user_registration(form: UserForm):
    """
    Register a user if all fields are properly filled
    """
    if form.validate_on_submit():
        email, password, firstname, lastname, \
        birthdate, photo, badwords, _ = get_form_fields(form)
       
        birthdate =  birthdate.strftime('%d/%m/%Y')
        response = UserManager.create_user(
            email, password, firstname,
            lastname, birthdate, photo
        )
        if response.status_code == 201:
            user_id = response.json()['body']['id']
            # in this case the request is ok!
            # after a successful registration, a message appears in the same page
            # inviting the just registered user to login
            UserManager.create_badwords(user_id, badwords.split(', '))
            return render_template('register.html', 
                mphoto = photo,
                form = form, 
                just_registered = "You are registered! Please")
        elif response.status_code == 200:
            # user already exists
            return render_template('register.html', form = form, 
                mphoto = photo,
                email_error_message = "Email already registered.")
        else:
            return render_template('register.html', form = form,
                mphoto = photo,
                email_error_message = "Invalid email."
            )
    # case in which the date format is incorrect
    else:
        for field, error in form.errors.items():
            # wrong dath of birth inserted and
            # check if the user with this email is already registered
            return render_template('register.html', form = form, 
                mphoto = DEFAULT_PIC, 
                date_error_message = field + ': ' + error[0])



def edit_profile():
    """
    Post request to edit
    """
    form = UserForm()
    # the email is not editable 
    # so manual fill this field to avoid error on submit
    form.email.data = current_user.email
    #points = current_user.points
    if form.validate_on_submit():
        # update user info
        _, password, firstname, lastname, \
        birthdate, photo, badwords, blacklist = get_form_fields(form)
        birthdate =  birthdate.strftime('%d/%m/%Y')
        updated_user = UserManager.update_user(
            current_user.email, current_user.id, password, firstname,
            lastname, birthdate, photo
        )
        updated_badwords = UserManager.update_badwords(current_user.id, badwords.split(', '))
        updated_blacklist = UserManager.update_blacklist(current_user.id, blacklist.split(', '))

        #if response.status_code == 200: 
        # update current user
        current_user.photo = updated_user.photo
        current_user.first_name = updated_user.first_name
        current_user.last_name = updated_user.last_name
        current_user.birthdate = updated_user.birthdate
        # user = UserManager.get_user_by_id(current_user.id)
        # display a message advising correct info update
        return render_template("profile.html", 
            mphoto = current_user.photo,
            form = fill_form_with_user(current_user, updated_badwords, updated_blacklist), 
            just_edited = "Personal info updated. Return to ")
    # wrong date format
    else:
        return render_template("profile.html", 
            form = fill_form_with_user(current_user), 
            date_error_message = "Date format DD/MM/YYYY.")

def show_profile():
    """
    Open a page with user infos
    """
    badwords = UserManager.get_badwords_by_user_id(current_user.id)
    blacklist = UserManager.get_blacklist_by_user_id(current_user.id)
    form = fill_form_with_user(current_user, badwords, blacklist)
    suggest = "README: separate each forbidden word and each blacklisted user with a ','"
    return render_template("profile.html", 
        mphoto = current_user.photo, 
        form = form, 
        suggest = suggest)


def fill_form_with_user(user, badwords, blacklist):
    """
    Programatically fill the UserForm with a User
    """
    form = UserForm()
    form.email.data = user.email
    form.firstname.data = user.first_name
    form.lastname.data = user.last_name
    form.points.data = user.points
    try:
        date = datetime.strptime(user.birthdate, "%Y-%m-%dT%H:%M:%SZ")
        date = date.strftime('%d/%m/%Y')
        form.birthdate.data = datetime.strptime(date, "%d/%m/%Y")
    except: 
        form.birthdate.data = datetime.strptime(user.birthdate, "%d/%m/%Y")
    form.badwords.data = ', '.join(badwords)
    form.blacklist.data = ', '.join(blacklist)
    return form