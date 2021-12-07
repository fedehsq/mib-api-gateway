from .view_test import ViewTest
from faker import Faker


class TestHome(ViewTest):
    faker = Faker()

    BASE_URl = 'http://localhost'

    @classmethod
    def setUpClass(cls):
        super(TestHome, cls).setUpClass()

    def test_home(self):
        user = self.login_test_user()
        rv = self.client.get(self.BASE_URL+'/')
        print(rv.json)
        assert rv.status_code == 302

        #rv = self.client.get(self.BASE_URL+'/logout')


    def test_profile(self):
        rv = self.client.get(self.BASE_URL+'/profile')
        #assert rv.text["url"] == 302

        user = self.login_test_user()
        rv = self.client.get(self.BASE_URL+'/')
        assert rv.status_code == 302
        print(user)
        print("fino a qui")
        rvo = self.client.get(self.BASE_URL+'/profile')
        #print(rvo.json())
        assert rvo.status_code == 200
    
    
    def test_logout(self):
        rv = self.client.get(self.BASE_URL+'/logout')
        assert rv.status_code == 200
     
    def test_logout2(self):
        rv = self.client.get(self.BASE_URL+'/logout')
        assert rv.status_code == 200
    