from unittest.mock import Mock, patch
from flask import current_app
from faker import Faker
from random import randint, choice
from werkzeug.exceptions import HTTPException
import requests
from .rao_test import RaoTest


class TestLotteryManager(RaoTest):

    faker = Faker('it_IT')
   
    def setUp(self):
        super(TestLotteryManager, self).setUp()
        from mib.rao.user_manager import UserManager
        from mib.rao.lottery_manager import LotteryManager

        self.user_manager = UserManager
        self.lottery_manager = LotteryManager

        from mib import app
        self.app = app    
    
    
    
    def test_create_lottery_play(self):
        response = self.lottery_manager.create_lottery_play(self.faker.pyint(1,99),self.faker.pyint(1,99))
        assert response.status_code == 302

    def test_already_exist_lottery(self):
        lottery_id = self.faker.pyint(1,99)
        response = self.lottery_manager.create_lottery_play(lottery_id,self.faker.pyint(1,99))
        response = self.lottery_manager.already_exists(lottery_id)
        response = self.lottery_manager.already_exists(5)
