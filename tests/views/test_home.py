from .view_test import ViewTest
from faker import Faker


class TestHome(ViewTest):
    faker = Faker()

    BASE_URl = 'http://localhost'

    @classmethod
    def setUpClass(cls):
        super(TestHome, cls).setUpClass()

    def test_user(self):
        user = self.create_test_user()
        self.login_test_user(user)
                   

        """rv = self.client.get(self.BASE_URL+'/')
        print(rv.json)
        assert rv.status_code == 200"""

        #rv = self.client.get(self.BASE_URL+'/logout')
    
    def test_inbox(self):
        self.get_inbox()
    
    def test_sent(self):
        self.get_sent()
        
    def test_scheduled(self):
        self.get_scheduled()
    
    def test_draft(self):
        self.get_draft()
    
    def test_mailbox(self):
        self.get_mailbox()
        #user, password = self.create_test_user()
        #self.login_test_user(user, password)
    
    def test_message(self):
        self.get_message()
    
    def test_profile(self):
        self.get_profile()
        self.edit_profile()
    
    def test_lottery(self):
        self.play_lottery()
 
    def test_report(self):
        self.report_user()