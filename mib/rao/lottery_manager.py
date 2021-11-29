import re
from requests.api import request
from mib import app
from flask import abort, redirect, render_template
from flask import abort, json, jsonify
from mib.forms.lottery import LotteryForm
import requests

class LotteryManager:
    LOTTERY_ENDPOINT = app.config['LOTTERY_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def create_lottery_play(cls,
                    id: int, number: int):
        try:
            url = "%s/lottery" % cls.LOTTERY_ENDPOINT
            response = requests.post(url,
                                     json={
                                         'id': id,
                                         'lottery_number': number
                                     },
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                     )
            print(response.status_code)
            if response.status_code == 201:
                # in this case the request is ok!
                return redirect('/')
            elif response.status_code == 200:
                form = LotteryForm()
                return render_template('lottery.html', form = form, error_number='Number not allowed.')
            else:
                form = LotteryForm()
                return render_template('lottery.html', form = form, error_number='Default error.')


        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(e)
            return abort(500)

    @classmethod
    def already_exists(cls, id:int):
        try:
            url = "%s/lottery/exist/%s" % (cls.LOTTERY_ENDPOINT, str(id))
            response = requests.get(url,
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            print(response.status_code)
            if response.status_code == 200:
                # in this case the lottery play already exists!
                return True
            elif response.status_code == 404:
                # in this case the lottery play don't already exists!
                return False
            else:
                return 2 

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(e)
            return abort(500)
