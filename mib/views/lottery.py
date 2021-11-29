from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required, current_user)

from mib.forms.lottery import LotteryForm
from mib.rao.lottery_manager import LotteryManager


lottery = Blueprint('lottery', __name__)

def lottery_play(form):
    if form.validate_on_submit():
        number = form.data['number']

        response = LotteryManager.create_lottery_play(
            current_user.id,
            number
        )

    return response

def already_played(id_):
    response = LotteryManager.already_exists(id_)
    return response
        
#route to play lottery
@lottery.route('/Lottery', methods=['GET','POST'])
@login_required
def play_lottery():
    #check if user is authenticated 
    #if not current_user.is_authenticated:
    #    return redirect("/")
    form = LotteryForm()
    if request.method == 'POST':
        number = form.data['number']
        if number > 100 or number < 1:
            if(already_played(current_user.id)):
                return render_template('lottery.html', form = form, error_number = "Number not allowed! Please choose another number between 1 and 100", number = number)
            else:
                return render_template('lottery.html', form = form, error_number = "Number not allowed! Please choose another number between 1 and 100", number = 0 )    
        return lottery_play(form)
    else:
        if(already_played(current_user.id)):
            return render_template('lottery.html', form = form, number = 1)
        else:
            return render_template('lottery.html', form = form, number = 0)
  