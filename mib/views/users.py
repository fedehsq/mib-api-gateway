from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required, current_user)

from mib.forms.user import UserForm, ReportForm
from mib.rao.user_manager import UserManager
from mib.auth.user import User, DEFAULT_PIC
from base64 import b64encode

users = Blueprint('users', __name__)

# Register a user if all fields are properly filled
def user_registration(form):
    if form.validate_on_submit():
        email = form.data['email']
        password = form.data['password']
        firstname = form.data['firstname']
        lastname = form.data['lastname']
        birthdate = form.data['birthdate']
        date = birthdate.strftime('%Y-%m-%d')
        print(form.data['photo'])
        if form.data['photo']:
            photo = 'data:image/jpeg;base64,' + b64encode(form.data['photo'].read()).decode('utf-8')
        else:
            photo = DEFAULT_PIC

        response = UserManager.create_user(
            email,
            password,
            firstname,
            lastname,
            date,
            photo
        )

        if response.status_code == 201:
            # in this case the request is ok!
            
            
            #to_login = User.build_from_json(user["user"])
            #login_user(to_login)            
            
            # after a successful registration, a message appears in the same page
            # inviting the just registered user to login
            flash('Registered.')
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
            flash('Invalid email format.')
            return render_template('register.html', form = form,
                mphoto = photo,
                email_error_message = "Invalid email."
            )
    # case in which the date format is incorrect
    else:
        for fieldName, errorMessages in form.errors.items():
            print(fieldName)
            print(errorMessages)
        # wrong dath of birth inserted and
        # check if the user with this email is already registered
        flash('Invalid date format.')
        return render_template('register.html', form = form, 
            mphoto = DEFAULT_PIC, 
            date_error_message = "Date format DD/MM/YYYY.")

# Return filtered users
# List all searched users by name, surname or email
def search_users(searched_input):
    response = UserManager.search_users(searched_input)
    return response

    
# List all users to choose a recipient for a message
@users.route('/users')
def get_users():
    if current_user.is_authenticated:
        # get all users
        response = UserManager.get_all_users()
        # if a user wants to filter the list with parameter user input
        searched_input = request.args.get("search")
    else:
        return redirect("/login")
    if searched_input:
        # filter and show the list
        users = search_users(searched_input)
        return render_template("users.html", users = users, current_user = current_user, searched_input="You searched: "+searched_input)
    else:
        # get all users list
        return render_template("users.html", users = response, current_user = current_user)

# Report a user
@users.route("/users/report/<email>", methods = ['GET','POST'])
def report(email):
    # if the user isn't athenticated he can't send report,
    # so he will be redirect to the login page
    if not current_user.is_authenticated:
        return redirect("/login")
    form = ReportForm()
    if request.method == 'GET':
        form.email.data = email
        # get the form to report a user
        return render_template('report.html', form = form)
    else:
        if form.validate_on_submit():
            email = form.data["email"]
            reported_user = UserManager.report(email)
            
            # check if exists the user, if not redirect to report page again
            if reported_user is None:
                return render_template('report.html', form = form, email_error_message = 'No user with this email.')
            else:
                return redirect("/")

@users.route('/register', methods=['GET', 'POST'])
def create_user():
    """This method allows the creation of a new user into the database

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


@users.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """Deletes the data of the user from the database.

    Args:
        id_ (int): takes the unique id as a parameter

    Returns:
        Redirects the view to the home page
    """

    response = UserManager.delete_user(id)
    if response.status_code != 202:
        flash("Error while deleting the user")
        return redirect(url_for('auth.profile', id=id))
        
    return redirect(url_for('home.index'))

