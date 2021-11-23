from flask import Blueprint, redirect, render_template
from flask_login import login_required, login_user, logout_user, current_user
from mib.forms import LoginForm
from mib.rao.user_manager import UserManager

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    This method allows the users to log in in the system
    Returns:
        Redirects the view to the home page
    """
    # check if the user is already logged, 
    # if so the user will be redirected to his dashboard
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        user, code = UserManager.authenticate_user(email, password)
        if code == 403:
            # blocked user
            return render_template('login.html', form = form, 
                user_blocked = "You are blocked, you can't login anymore.")
        elif user and code == 200:
            # valid user
            login_user(user)
            return redirect('/')
        else:
            # deleted or wrong credentials
            return render_template('login.html', form = form, 
                wrong_credentials = "Incorrect username or password.")

    return render_template('login.html', form = form)

@auth.route('/logout')
@login_required
def logout():
    """
    This method allows the users to log out of the system
    Returns:
        Redirects the view to the home page
    """
    logout_user()
    return redirect('/')