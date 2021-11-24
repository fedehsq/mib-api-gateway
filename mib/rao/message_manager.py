from requests.api import request
from werkzeug.exceptions import ServiceUnavailable
from mib import app
from flask_login import (logout_user)
from flask import abort, json, jsonify
import requests

class MessageManager:
    MESSAGES_ENDPOINT = app.config['MESSAGES_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']
    @classmethod
    def get_mailbox(cls):
        """ This method contacts the message microservice and 
        retrieves the mailbox
        """
        try:
            response = requests.get("%s/get_messages" % (cls.MESSAGES_ENDPOINT), json={"email":"example@example.com","op":"inbox"}, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            #if response.status_code == 201:
                # I get the dict of users and I retrieve each user from json
                # and I save all Users in a list
            print(json_payload)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(e)
            return abort(500)
        return 0
                