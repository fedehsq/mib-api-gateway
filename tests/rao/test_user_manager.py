from unittest.mock import Mock, patch
from flask import current_app
from faker import Faker
from random import randint, choice
from werkzeug.exceptions import HTTPException
import requests


from mib.auth.user import User
from .rao_test import RaoTest


class TestUserManager(RaoTest):

    faker = Faker('it_IT')

    def setUp(self):
        super(TestUserManager, self).setUp()
        from mib.rao.user_manager import UserManager
        from mib.rao.lottery_manager import LotteryManager

        self.user_manager = UserManager
        self.lottery_manager = LotteryManager

        from mib import app
        self.app = app

    def generate_user(self, type):
    
        data = {
            'id': randint(0, 999),
            'email': TestUserManager.faker.email(),
            #'is_active' : choice([True,False]),
            #'authenticated': choice([True,False]),
            #'is_anonymous': False,
            'first_name': "Mario",
            'last_name': "Rossi",
            'birthdate': TestUserManager.faker.date_of_birth().strftime("%d/%m/%Y"),
            'type': type,
            'points': "0",
            'photo': "jpeg"
        }

        user = User(**data)
        return user

    def test_create_user(self):
        user = self.generate_user('operator')
        password = self.faker.password()
        response = self.user_manager.create_user(user.email, password, user.first_name,user.last_name,user.birthdate, user.photo)
        assert response != None

    def test_update_user(self):
        user = self.generate_user('operator')
        password = self.faker.password()
        response = self.user_manager.create_user(user.email, password, user.first_name,user.last_name,user.birthdate, user.photo)
        assert response != None
        response = self.user_manager.update_user(user.email, user.id, password, "pippo", user.last_name,user.birthdate, user.photo)
        assert response != None
    
    def test_report_user(self):
        user = self.generate_user('operator')
        password = self.faker.password()
        response = self.user_manager.create_user(user.email, password, user.first_name,user.last_name,user.birthdate, user.photo)
        response = self.user_manager.report(user.email)
        assert response == 200
        response = self.user_manager.report("user.mail")
        assert response == 404
        
    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_id(self, mock_get):
        user = self.generate_user(type='operator')
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthdate': user.birthdate,
            'photo': user.photo,
            'points': user.points
            #'is_active': False,
            #'authenticated': False,
            #'is_anonymous': False,
            #'type': user.type
        }
        mock_get.return_value = Mock(
            status_code=200,
            json = lambda:{
                'body':user_data
            }
        )
        response = self.user_manager.get_user_by_id(id)
        assert response is not None

    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_id_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        with self.assertRaises(HTTPException) as http_error:
            self.user_manager.get_user_by_id(randint(0, 999))
            self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_email(self, mock_get):
        user = self.generate_user(type='customer')
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthdate': user.birthdate,
            'photo': user.photo,
            'points': user.points
            #'is_active': False,
            #'authenticated': False,
            #'is_anonymous': False,
            #'type': user.type
        }

        mock_get.return_value = Mock(
            status_code=200,
            json = lambda:{
                'body': user_data
            }
        )
        response = self.user_manager.get_user_by_email(user.email)
        assert response is not None
    
    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_email_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        email = TestUserManager.faker.email()
        with self.assertRaises(HTTPException) as http_error:
            self.user_manager.get_user_by_email(email)
            self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.delete')
    def test_delete_user(self, mock_get):
        user = self.generate_user(type='operator')
        mock_get.return_value = Mock(status_code=200)        

        with self.app.test_request_context ():
            response = self.user_manager.delete_user(user_id=user.id)            
            assert response is not None

    @patch('mib.rao.user_manager.requests.delete')
    def test_delete_user_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        with self.app.test_request_context ():
            with self.assertRaises(HTTPException) as http_error:
                self.user_manager.delete_user(user_id=randint(0,999))
                self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.post')
    def test_authenticate_user(self, mock_post):        
        user = self.generate_user(type='operator')
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthdate': user.birthdate,
            'photo': user.photo,
            'points': user.points
        }
        mock_post.return_value = Mock(
            status_code=200,
            json = lambda:{
                'body': user_data
            }
        )
        password = TestUserManager.faker.password()
        response = self.user_manager.authenticate_user(
            email=user.email, password=password
        )
        assert response is not None

    @patch('mib.rao.user_manager.requests.post')
    def test_authenticate_user_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        mock_post.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        with self.app.test_request_context ():
            with self.assertRaises(HTTPException) as http_error:
                self.user_manager.authenticate_user(
                    self.faker.email(),
                    self.faker.password()
                )
                self.assertEqual(http_error.exception.code, 500)
    
    def test_create_badwords(self):
        user = self.generate_user('operator')
        password = self.faker.password()
        response = self.user_manager.create_user(user.email, password, user.first_name,user.last_name,user.birthdate, user.photo)
        json = response.json()
        u = json['body']
        r = self.user_manager.create_badwords(u['id'], ["Badword1"])
        assert r == ["Badword1"]
        r = self.user_manager.update_badwords(u['id'], ["Badword2"])    
        assert r == ["Badword2"]
        r = self.user_manager.delete_badwords(u['id'])
        assert r.status_code == 202


    def test_create_blacklist(self):
        user = self.generate_user('operator')
        password = self.faker.password()
        response = self.user_manager.create_user(user.email, password, user.first_name,user.last_name,user.birthdate, user.photo)
        json = response.json()
        u = json['body']
        r = self.user_manager.create_blacklist(u['id'], ["a@b.commm"])
        assert r == []

        r = self.user_manager.update_blacklist(u['id'], ["a@b.comm"])
        assert r == []

        r = self.user_manager.delete_blacklist(u['id'])
        assert r.status_code == 202

    
