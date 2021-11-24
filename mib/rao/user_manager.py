from requests.api import request
from werkzeug.exceptions import ServiceUnavailable
from mib.auth.user import User
from mib import app
from flask_login import (logout_user)
from flask import abort, json
import requests

class UserManager:
    USERS_ENDPOINT = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    # This method contacts the user microservice and 
    # retrieves all the registered users that correspond 
    # to the searched input
    def search_users(cls, searched_input):
        try: 
            response = requests.post("%s/search_users/%s" % (cls.USERS_ENDPOINT, str(searched_input)), timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                users = [User.build_from_json(item) for item in json_payload.get('searched_users')]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return users    

    @classmethod
    # This method contacts the user microservice to
    # report a user, if it exists
    def report(cls, email):
        try:
            response = requests.post("%s/report/%s" % (cls.USERS_ENDPOINT, str(email)), timeout= cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                reported_user = User.build_from_json(json_payload)
            if response.status_code == 404:
                reported_user = None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return reported_user    


    @classmethod
    def get_all_users(cls):
        """ This method contacts the user microservice and 
        retrieves all the registered users except for the one
        who is logged
        """
        try:
            response = requests.get("%s/users" % (cls.USERS_ENDPOINT), timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                # I get the dict of users and I retrieve each user from json
                # and I save all Users in a list
                users = [User.build_from_json(item) for item in json_payload.get('users_response')] 
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return users
                
    @classmethod
    def get_user_by_id(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                user = User.build_from_json(json_payload)
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return user                

    @classmethod
    def get_badwords_by_user_id(cls, user_id: int):
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/badwords/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                badwords = json_payload['badwords']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return badwords

    @classmethod
    def get_blacklist_by_user_id(cls, user_id: int):
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/blacklist/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            print(json_payload)
            if response.status_code == 200:
                # json_payolad is a couple: blacklisted person and response status
                # if response status is 404, 
                # the blacklisted user doesn't exist
                # so it won't be in the final list
                blacklist = [User.build_from_json(person) for person in json_payload.get('blacklist')]
                # blacklist = [User.build_from_json(person[0]) for person in json_payload if person[1] != 404]
                # blacklist = json_payload['blacklist']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return blacklist


    @classmethod
    def get_user_by_email(cls, user_email: str):
        """
        This method contacts the users microservice
        and retrieves the user object by user email.
        :param user_email: the user email
        :return: User obj with email=user_email
        """
        try:
            response = requests.get("%s/user_email/%s" % (cls.USERS_ENDPOINT, user_email),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            user = None

            if response.status_code == 200:
                user = User.build_from_json(json_payload)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    @classmethod
    def create_user(cls,
                    email: str, password: str,
                    firstname: str, lastname: str,
                    birthdate: str, photo:str,
                    badwords: str):
        try:
            
            url = "%s/user" % cls.USERS_ENDPOINT
            response = requests.post(url,
                                     json={
                                         'email': email,
                                         'password': password,
                                         'firstname': firstname,
                                         'lastname': lastname,
                                         'birthdate': birthdate,
                                         'photo': photo,
                                         'badwords': badwords
                                     },
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                     )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return response

    @classmethod
    def update_user(cls, user_id: int, password: str,
                    firstname: str, lastname: str,
                    birthdate, photo:str,
                    badwords: str, blacklist: str):
        """
        This method contacts the users microservice
        to allow the users to update their profiles
        :param password:
        :param email:
        :param user_id: the customer id
            email: the user email
            password: the user password
        :return: User updated
        """
        try:
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.put(url,
                                    json={
                                        'password': password,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'birthdate': birthdate,
                                        'photo': photo,
                                        'badwords': badwords,
                                        'blacklist' : blacklist
                    
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def delete_user(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the account of the user
        :param user_id: the user id
        :return: User updated
        """
        try:
            logout_user()
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.delete(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        """
        This method authenticates the user trough users AP
        :param email: user email
        :param password: user password
        :return: None if credentials are not correct, User instance if credentials are correct.
        """
        payload = dict(email=email, password=password)
        try:
            print('trying response....')
            response = requests.post('%s/authenticate' % cls.USERS_ENDPOINT,
                                     json=payload,
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                     )
            print('received response....')
            json_response = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)

        if response.status_code == 401:
            # user is not authenticated
            return None, 401
        elif response.status_code == 403:
            # user is blocked
            return None, 403
        elif response.status_code == 200:
            user = User.build_from_json(json_response['user'])
            return user, 200
        else:
            raise RuntimeError(
                'Microservice users returned an invalid status code %s, and message %s'
                % (response.status_code, json_response['error_message'])
            )
