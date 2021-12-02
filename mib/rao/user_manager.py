from requests.api import request
from werkzeug.exceptions import ServiceUnavailable
from mib.auth.user import User
from mib import app
from flask_login import (logout_user)
from flask import abort, jsonify
import requests


class UserManager:
    USERS_ENDPOINT = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']
    
    @classmethod
    def create(cls, user_id: int, path, body):
        """
        This method contacts the users microservice
        to allow the user with user_id to create his 'body'
        :return: the object created
        """
        try:
            url = "%s/%s/%s" % (cls.USERS_ENDPOINT, path, str(user_id))
            response = requests.post(url,
                                    json = {
                                        path: body,                  
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            if response.status_code == 201:
                json_payload = response.json()
                return json_payload['body']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def delete(cls, arg, user_id: int):
        """
        This method contacts the user ms and delete the 'arg'
        of the user with user_id
        :return: the response of user ms
        """
        if arg == 'user':
            logout_user()
        try:
            url = "%s/%s/%s" % (cls.USERS_ENDPOINT, arg, str(user_id))
            response = requests.delete(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return response
    
    @classmethod
    def update(cls, path, user_id: int, body):
        """
        This method contacts the user ms and updates the 'body'
        of the user with user_id
        :return: the object updated
        """
        try:
            url = "%s/%s/%s" % (cls.USERS_ENDPOINT, path, str(user_id))
            response = requests.put(url,
                                    json = {
                                        path: body,                    
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            if response.status_code == 200:
                json_payload = response.json()
                return json_payload['body']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def search_users(cls, searched_input):
        """
        This method contacts the user microservice and 
        retrieves all the registered users that correspond 
        to the searched input
        """
        try: 
            response = requests.post("%s/search_users/%s" % (cls.USERS_ENDPOINT, searched_input), 
                timeout = cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                users = [User.build_from_json(item) for item in json_payload.get('body')]
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return users    

    @classmethod
    def report(cls, email):
        """
        This method contacts the user microservice to
        report a user
        """
        try:
            response = requests.post("%s/report/%s" % (cls.USERS_ENDPOINT, email), 
                timeout = cls.REQUESTS_TIMEOUT_SECONDS)
            #json_payload = response.json()
            if response.status_code == 200:
                return 200
            elif response.status_code == 404:
                return 404
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)


    @classmethod
    def get_all_users(cls):
        """ 
        This method contacts the user microservice and 
        retrieves all the registered users
        """
        try:
            response = requests.get("%s/users" % (cls.USERS_ENDPOINT), timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                # Get the dict of users and retrieve each user from json
                users = [User.build_from_json(item) for item in json_payload.get('body')]  
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
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
                user = User.build_from_json(json_payload['body'])
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return user                

    @classmethod
    def get_badwords_by_user_id(cls, user_id: int):
        """
        This method contacts the users microservice
        and retrieves the user's badwords by user id.
        :param user_id: the user id
        :return: the list of badwords of the user with user_id
        """
        try:
            response = requests.get("%s/badwords/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                badwords = json_payload['body']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return badwords

    @classmethod
    def get_blacklist_by_user_id(cls, user_id: int):
        """
        This method contacts the users microservice
        and retrieves the user's blacklist by user id.
        :param user_id: the user id
        :return: the blacklist for the user with id=user_id
        """
        try:
            response = requests.get("%s/blacklist/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                blacklist = [email for email in json_payload.get('body')]
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
        :return: User obj with email = user_email
        """
        try:
            response = requests.get("%s/user_email/%s" % (cls.USERS_ENDPOINT, user_email),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return User.build_from_json(json_payload['body'])
            else: 
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def create_user(cls,
                    email: str, password: str,
                    firstname: str, lastname: str,
                    birthdate: str, photo: str):
        """
        This method contacts the users microservice
        and creates the user 
        :param user_email: the user's email
        :param password: the user's password
        :param firstname: the user's firstname
        :param lastname: the user's lastname
        :param birthdate: the user's birthdate
        :param photo: the user's profile pic base64 encoded
        :return: User obj
        """
        try:
            url = "%s/user" % cls.USERS_ENDPOINT
            response = requests.post(url,
                                    json = {
                                        'email': email,
                                        'password': password,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'birthdate': birthdate,
                                        'photo': photo,
                                    },
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS
                                    )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return response

    @classmethod
    def update_user(cls, email, user_id: int, password: str,
                    firstname: str, lastname: str,
                    birthdate, photo:str):
        """
        This method contacts the users microservice
        to allow the users to update their profiles
        :param user_email: the user's email
        :param password: the user's password
        :param firstname: the user's firstname
        :param lastname: the user's lastname
        :param birthdate: the user's birthdate
        :param photo: the user's profile pic base64 encoded
        :return: User obj
        """
        try:
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.put(url,
                                    json = {
                                        'email': email,
                                        'password': password,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'birthdate': birthdate,
                                        'photo': photo,
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            if response.status_code == 200:
                json_payload = response.json()
                return User.build_from_json(json_payload['body'])
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def create_badwords(cls, user_id: int, badwords):
        """
        This method contacts the users microservice
        to allow the user with user_id to create his badwords list
        :return: Badwords list created
        """
        return UserManager.create(user_id, 'badwords', badwords)

    @classmethod
    def update_badwords(cls, user_id: int, badwords):
        """
        This method contacts the users microservice
        to allow the user with user_id to update his badwords list
        :return: Badwords list updated
        """
        return UserManager.update('badwords', user_id, badwords)
    
    @classmethod
    def delete_badwords(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the badwords list for the user with user_id as id
        :param user_id: the user id
        :return: result of the operation
        """
        return UserManager.delete('badwords', user_id)
    
    @classmethod
    def create_blacklist(cls, user_id: int, blacklist):
        """
        This method contacts the users microservice
        to allow the user with user_id to create his blacklist
        :return: The created blacklist
        """
        return UserManager.create(user_id, 'blacklist', blacklist) 

    @classmethod
    def update_blacklist(cls, user_id: int, blacklist):
        """
        This method contacts the users microservice
        to allow the user with user_id to update his blacklist
        :return: blacklist updated
        """
        return UserManager.update('blacklist', user_id, blacklist)

    @classmethod
    def delete_blacklist(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the blacklist for the user with user_id as id
        :param user_id: the user id
        :return: result of the operation
        """
        return UserManager.delete('blacklist', user_id)

    @classmethod
    def delete_user(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the account of the user
        :param user_id: the user id
        :return: the result of the operation
        """
        return UserManager.delete('user', user_id)

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        """
        This method contacts the users microservice to authenticate the user
        :param email: user email
        :param password: user password
        :return: None if an error occurs, User instance if credentials are correct.
        """
        payload = dict(email = email, password = password)
        try:
            response = requests.post('%s/authenticate' % cls.USERS_ENDPOINT,
                                    json = payload,
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            json_response = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)
        if response.status_code == 404:
            # user not found
            return None, 404
        elif response.status_code == 403:
            # user is blocked
            return None, 403
        elif response.status_code == 200:
            user = User.build_from_json(json_response['body'])
            return user, 200
        elif response.status_code == 400:
            return None, 400
        else:
            raise RuntimeError(
                'Microservice users returned an invalid status code %s, and message %s'
                % (response.status_code, json_response['message'])
            )
