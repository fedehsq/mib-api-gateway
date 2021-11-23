from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user
from mib.forms import LoginForm
from mib.rao.user_manager import UserManager

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login(re=False):
    print(current_user)
    # check if the user is already logged, 
    # if so the user will be redirected to his dashboard
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        user = UserManager.authenticate_user(email, password)
        if user is not None and user.deleted == False:
            if user.is_blocked:
                return render_template('login.html', form = form, 
                    user_blocked = "You are blocked, you can't login anymore.")
            login_user(user)
            return redirect('/')
        else:
            # tells to the user that he inserted wrong credentials
            flash("Invalid credentials")
            return render_template('login.html', form = form, 
                wrong_credentials = "Incorrect username or password.")

    return render_template('login.html', form = form)


@auth.route('/logout')
@login_required
def logout():
    """This method allows the users to log out of the system

    Returns:
        Redirects the view to the home page
    """
    logout_user()
    return redirect('/')

# Unsubscribe
@auth.route("/delete")
@login_required
def delete():
    id = current_user.id
    response = UserManager.delete_user(id)
    return render_template('delete.html')
   
   
