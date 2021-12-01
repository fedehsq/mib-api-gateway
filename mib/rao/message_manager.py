from requests.api import get, request
from werkzeug.exceptions import ServiceUnavailable
from mib import app
from flask import abort, json, jsonify
from mib.rao.user_manager import UserManager
from mib.rao.message import Message
import requests

class MessageManager:
    MESSAGES_ENDPOINT = app.config['MESSAGES_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_filtered_messages(cls, user_email, body, sender, date):
        """
        This method contacts the messages microservice
        and search the messages of the user whose user email == user_email.
        :return: messages that match with one or more parameters
        """
        try:
            url = "%s/search/%s" % (cls.MESSAGES_ENDPOINT, user_email)
            response = requests.post(url,
                                    json = {
                                        'body': body,
                                        'sender': sender,
                                        'date': date
                                    },
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            json_payload = response.json()
            if response.status_code == 200:
                filtered_inbox = [Message.build_from_json(message) for message in json_payload['body']['filtered_inbox']]
                filtered_sent = [Message.build_from_json(message) for message in json_payload['body']['filtered_sent']]
                filtered_scheduled = [Message.build_from_json(message) for message in json_payload['body']['filtered_scheduled']]
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        return filtered_inbox, filtered_sent, filtered_scheduled


    @classmethod
    def create_message(cls, message: Message):
        """
        This method contacts the messages microservice
        and create the message object for the user 
        with email = message.sender.
        :param message: the lightweight message 
        :return: the new message
        """
        try:
            url = "%s/message/%s" % (cls.MESSAGES_ENDPOINT, message.sender)
            response = requests.post(url,
                                    json = message.serialize(),
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            json_payload = response.json()
            if response.status_code == 201:
                return Message.build_from_json(json_payload['body'])
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)


    @classmethod
    def update_message(cls, message: Message):
        """
        This method contacts the messages microservice
        and update the message object by user email == message.sender.
        :param message: the lightweight message 
        :return: the edited message
        """
        try:
            url = "%s/message/%s" % (cls.MESSAGES_ENDPOINT, message.sender)
            response = requests.put(url,
                                    json = message.serialize(),
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            json_payload = response.json()
            if response.status_code == 200:
                return Message.build_from_json(json_payload['body'])
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        
    @classmethod
    def get_message_by_id(cls, message_id: int) -> Message:
        """
        This method contacts the messages microservice
        and retrieves the message object by message id.
        :param message_id: the message id
        :return: Message obj with id = message_id
        """
        try:
            response = requests.get("%s/message/%s" % (cls.MESSAGES_ENDPOINT, str(message_id)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return Message.build_from_json(json_payload['body'])
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def get_dir(cls, dir, email):
        """ 
        This method contacts the message microservice and 
        retrieves the messages in the 'dir' box
        """
        try:
            response = requests.get("%s/%s/%s" % (cls.MESSAGES_ENDPOINT, dir, email),
                timeout = cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return [Message.build_from_json(message) for message in json_payload['body']]
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def get_inbox(cls, email):
        """ 
        This method contacts the message microservice and 
        retrieves the inbox messages
        :param email: the user email who requests the inbox messages
        :return: json message containing these messages
        """
        return MessageManager.get_dir('inbox', email)
    
    @classmethod
    def get_scheduled(cls, email):
        """ 
        This method contacts the message microservice and 
        retrieves the scheduled messages
        :param email: the user email who requests the scheduled messages
        :return: json message containing these messages
        """
        return MessageManager.get_dir('scheduled', email)
    
    
    @classmethod
    def get_sent(cls, email):
        """ 
        This method contacts the message microservice and 
        retrieves the draft messages
        :param email: the user email who requests the sent messages
        :return: json message containing these messages
        """
        """user = UserManager.get_user_by_email(email)
        if user is None:
            return {
                'status': 'failure',
                'message': 'User not found',
            }"""
        return MessageManager.get_dir('sent', email)
    
    
    @classmethod
    def get_draft(cls, email):
        """ 
        This method contacts the message microservice and 
        retrieves the draft messages
        :param email: the user email who requests the messagese
        :return: json message containing these messages
        """
        return MessageManager.get_dir('draft', email)
    
    
    @classmethod
    def get_notifications_number(cls, email):
        """ 
        This method contacts the message microservice and 
        retrieves the notifications number
        :param email: the user email who requests the notifications
        :return: json message containing these numbers
        """
        try:
            response = requests.get("%s/notifications/%s" % (cls.MESSAGES_ENDPOINT, email),
                timeout = cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload['body']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    
    @classmethod
    def delete_message_by_id(cls, message_id):
        """
        This method contacts the message microservice
        to delete the account of the user
        :param message_id: the message id
        """
        try:
            url = "%s/message/%s" % (cls.MESSAGES_ENDPOINT, str(message_id))
            return requests.delete(url, timeout = cls.REQUESTS_TIMEOUT_SECONDS)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    