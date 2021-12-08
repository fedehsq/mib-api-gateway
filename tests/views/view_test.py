import unittest
from faker import Faker
from random import choice, randint
from bs4 import BeautifulSoup
from mib.rao.message import Message
from mib.auth.user import User

# LOGIN KEYWORDS:
LOGIN_PAGE_TITLE = 'My message in a bottle'
USERNAME = 'Admin'
WRONG_CREDENTIALS = 'Incorrect username or password.'
EMAIL_NOT_REGISTERED = 'Email not registered.'
INVALID_EMAIL = 'email: Invalid email address.'
INVALID_PASSWORD = 'password: Field must be at least 5 characters long.'

# REGISTER KEYWORDS:
REGISTRATION_PAGE_TITLE = 'Registration'
REGISTRATION_DONE = 'You are registered! Please log in.'
WRONG_EMAIL = 'Email already registered.'
WRONG_DATE = 'birthdate: Not a valid date value'

# PROFILE PAGE KEYWORDS:
PROFILE_PAGE_TITLE = 'Profile'
UPDATE_DONE = 'Personal info updated. Return to dashboard'

# UNSUBSCRIBED PAGE KEYWORDS
UNSUBSCRIBED_PAGE_TITLE = 'Unsubscribed'

# MESSAGE KEYWORDS
MSG_CREATION_PAGE_TITLE = "Message"
MSG_DRAFT = 'Draft! back to homepage.'
MSG_SCHEDULED = 'Scheduled! back to homepage.'
WRONG_DATE_TIME = 'Date format DD/MM/YYYY hh:mm'
WRONG_WORDS = 'Change body!'

# MAILBOX KEYWORDS
MAILBOX = "Mailbox"
INBOX = "Inbox"
SENT = "Sent"
SCHEDULED = "Scheduled"
DRAFT = 'Draft'

# REPORT
REPORT = "User report"
WRONG_REPORT_EMAIL = "No user with this email."
REPORT_PAGE_TITLE = "User report"


# LOTTERY
LOTTERY_PAGE_TITLE = "Play Lottery"
LOTTERY_ERROR_NUMBER = "Number not allowed! Please choose another number between 1 and 100"

# ----- Auxiliary functions used in the tests ------ 

# Get the requested page, an unique id is assigned in one field
# on the html page to recognize the field with which to test.
def get_page_id(app, page, html_id):
    # Request the page
    response = app.get(page, follow_redirects = True)
    # extract the html page from the response
    html = str(response.data, 'utf8')
    # parse this page
    soup = BeautifulSoup(html, 'html.parser')
    # access and return the interesting field to check
    message = soup.find(id = html_id).text
    return message

# Try to post on the requested page, an unique id is assigned in one field
# on the html page to recognize the field with which test.
def post_and_get_result_id(app, page, data, html_id):
    # Pass the parameters that will fill the login form: 
    # in case of successfully login, generally, a message appears on the 
    # requested page or there will be a redirection to another page,
    # otherwise an error message appears on this page.
    # These possibilities are tested to understand the response.
    response = app.post(page, 
        data = data, 
        follow_redirects = True)
    # extract the html page from the response
    html = str(response.data, 'utf8')
    # parse this page
    soup = BeautifulSoup(html, 'html.parser')
    # access and return the interesting field to check
    message = soup.find(id = html_id).text
    return message

# Try to register an user, an unique id is assigned in one field
# on the html page to recognize the field with which test.
def post_register(app, email, firstname, lastname, password, date_of_birth, photo, html_id): 
    # Pass the parameters that will fill the registration form.
    # In case of successfully registration, a message appears on the 
    # screen that suggest to the user to go to the login page.
    # In case of incorrect registration, two messages can appears in this page.
    #   1: email already used
    #   2: wrong date format
    # These messages are checked to test the proper case (success or kind of error).

    return post_and_get_result_id(app, 'http://localhost/register', 
        {'email': email, 'firstname': firstname, 'lastname': lastname, 
        'password': password, 'birthdate': date_of_birth, 'badwords' : 'evil, devil'}, 
        html_id)

# Try to login an user, an unique id is assigned in one field
# on the html page to recognize the field with which test.
def post_login(app, email, password, html_id):
    # Pass the parameters that will fill the login form: 
    # In case of successfully login, there will be a redirection to the homepage
    # otherwise an error message appears on this page (wrong username or password).
    # These two possibilities are tested to understand the response.
    return post_and_get_result_id(app, 'http://localhost/login', 
        {'email': email, 'password': password}, 
        html_id)


# Try to update an user info, an unique id is assigned in one field
# on the html page to recognize the field with which test.
def post_update_profile(app, email, firstname, lastname, password, date_of_birth, html_id): 
    # Pass the parameters that will fill the info profile form.
    # In case of successfully update, 
    # a message appears to the page (suggest to come back to dashboard)
    # In case of wrong form filling a message shows the error (only the date can be wrong)
    return post_and_get_result_id(app, '/profile', 
        {'email': email, 'firstname': firstname, 'lastname': lastname, 
        'password': password, 'birthdate': date_of_birth}, 
        html_id)


# Try to save/schedule a message, an unique id is assigned in one field
# on the html page to recognize the field with which test.
def post_message(app, receiver, body, date, time, choice, html_id):
    # Pass the parameters that will fill the message form: 
    # In case of successfully edits, there will be 2 different messages
    # according to the tapped button
    #   1. Draft ok
    #   2. Schedule ok
    # otherwise an error message appears on this page (wrong date/time).
    # These two possibilities are tested to understand the response.

    return post_and_get_result_id(app, '/message' + "/" + receiver, 
        {'receiver': receiver, 'body': body, 'date': date, 
        'time': time, 'choice': choice}, 
        html_id)

# Edit a message through message id
def post_edit_message(app, receiver, body, date, time, choice, message_id, html_id):
    # Pass the parameters that will fill the message form: 
    # In case of successfully edits, there will be 2 different messages
    # according to the tapped button
    #   1. Draft ok
    #   2. Schedule ok
    # otherwise an error message appears on this page (wrong date/time).
    # These two possibilities are tested to understand the response.
    return post_and_get_result_id(app, '/mailbox/draft/' + message_id, 
        {'receiver': receiver, 'body': body, 'date': date, 
        'time': time, 'choice': choice}, 
        html_id)

# Try to report a user
def post_report(app, email, reason, html_id):
    page = '/users/report/' + email
    return post_and_get_result_id(app, page, 
        {'email': email, 'reason': reason}, html_id)

# Try to post a lottery number
def post_lottery(app, number, html_id):
    return post_and_get_result_id(app, '/lottery', {'number': number}, html_id)

def generate_user():
    data = {
        'id': randint(0, 999),
        'email': ViewTest.faker.email(),
        'first_name': "Mario",
        'last_name': "Rossi",
        'birthdate': "17/12/2000",
        'points': "0",
        'photo': "jpeg"
    }
    user = User(**data)
    return user

class ViewTest(unittest.TestCase):
    faker = Faker()

    BASE_URL = "http://localhost"



    @classmethod
    def setUpClass(cls):
        from mib import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        from mib.rao.user_manager import UserManager
        cls.user_manager = UserManager
        from mib.rao.message_manager import MessageManager
        cls.message_manager = MessageManager

    def create_test_user(self):
        app = self.client
        # ------ GET: REGISTER PAGE ------
        response = get_page_id(app, '/register', 'page_title')
        self.assertEqual(response, REGISTRATION_PAGE_TITLE) 

        # ----- INCORRECT REGISTRATION: DATE OF BIRTH IN INCORRECT FORMAT ------
        response = post_register(app, 'a@b.com', 'a', 
            'b', 'abcdef', '055/06/98', 'base64photo', 'wrong_date')
        self.assertEqual(response, WRONG_DATE)
        
        # ----- INCORRECT REGISTRATION: SHORT PASSWORD ------
        response = post_register(app, 'a@b.com', 'a', 
            'b', 'abcd', '05/06/1998', 'base64photo', 'wrong_date')
        self.assertEqual(response, INVALID_PASSWORD)

        # ----- INCORRECT REGISTRATION: INVALID EMAIL ------
        response = post_register(app, 'a@b', 'a', 
            'b', 'abcde', '05/06/1998', 'base64photo', 'wrong_date')
        self.assertEqual(response, INVALID_EMAIL)
        
        # ---- REGISTER A VALID USER AND USE IT -----
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)

        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'wrong_email')
        self.assertEqual(response, WRONG_EMAIL)

        return user

    def login_test_user(self, user):
        """
        Simulate the customer login for testing the views with @login_required
        :return: customer
        """
        # ------ GET: LOGIN PAGE ------
        title = get_page_id(self.client, self.BASE_URL + '/login', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

        # ------ POST: CORRECT LOGIN -----
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)

        # ------ GET: LOGOUT -----
        title = get_page_id(self.client, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

        # ----- POST: INCORRECT LOGIN, WRONG CREDENTIALS ------
        wrong_credentials = post_login(self.client, 'pao@pao.com', 'bxdfghjkjh', 'wrong_credentials')
        self.assertEqual(wrong_credentials, EMAIL_NOT_REGISTERED)

        # ----- POST: INCORRECT LOGIN, EMAIL NOT REGISTERED ------
        wrong_credentials = post_login(self.client, 'paola@pao.com', 'bxdfghjkjh', 'wrong_credentials')
        self.assertEqual(wrong_credentials, EMAIL_NOT_REGISTERED)

        # ----- GET: LOGIN PAGE REQUEST WHEN THE CLIENT IS ALREADY LOGGED ------
        #with self.client:                
        post_login(self.client, user.email, 'password', 'username')
        username = get_page_id(self.client, self.BASE_URL + '/login', 'username')
        # Client is already logged and will be redirected to his dashboard
        self.assertEqual(username, user.first_name)
        title = get_page_id(self.client, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
    
    def logout(self):
         # ------ GET: LOGOUT -----
        title = get_page_id(self.client, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
    
    def get_inbox(self):
        app = self.client
        #title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)
        # ------ Test1: logged -----
        title = get_page_id(app, '/mailbox/inbox', 'page_title')
        self.assertEqual(title, INBOX)  
        # ------ Test1: logged -----
        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = user.id
        message.sender_id = user.id
        message.sender = user.email
        message.scheduled = True
        message.draft = True
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)
        title = get_page_id(app, '/mailbox/inbox/' + str(m.id), 'page_title')
        self.assertEqual(title, 'Message')

        # ------ GET: LOGOUT -----
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
        # ------ Test2: inbox with login -----
        title = get_page_id(app, '/mailbox/inbox', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
    def get_draft(self):
        app = self.client
        #title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)

        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = user.id
        message.sender_id = user.id
        message.sender = user.email
        message.scheduled = False
        message.draft = True
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)
        
         # ------ Test1: logged -----
        title = get_page_id(app, '/mailbox/draft/' + str(m.id), 'page_title')
        self.assertEqual(title, 'Message')

        from mib.views.message import draft_remove
        response = draft_remove(m)
        assert response == None
        response = draft_remove(None)

        # ------ Test5: inbox with existing id and delete-----
        response = post_and_get_result_id(app,'/mailbox/draft/',{"delete":m.id},"page_title")
        self.assertEqual(response, DRAFT)

       
        
        
        # ------ Test1: logged -----
        title = get_page_id(app, '/mailbox/draft', 'page_title')
        self.assertEqual(title, DRAFT)

        # ------ GET: LOGOUT -----
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
        # ------ Test2: inbox with login -----
        title = get_page_id(app, '/mailbox/draft', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

    def get_sent(self):
        app = self.client
        #title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)
        # ------ Test1: logged -----
        title = get_page_id(app, '/mailbox/sent', 'page_title')
        self.assertEqual(title, SENT)

        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = user.id
        message.sender_id = user.id
        message.sender = user.email
        message.scheduled = False
        message.draft = False
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        message.sent = 1
        message.read = 1
        m = self.message_manager.create_message(message)
        title = get_page_id(app, '/mailbox/sent/' + str(m.id), 'page_title')
        self.assertEqual(title, 'Message')

        # ------ GET: LOGOUT -----
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
        # ------ Test2: inbox with login -----
        title = get_page_id(app, '/mailbox/sent', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

    def get_scheduled(self):
        app = self.client
        #title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        user = generate_user()
        response = self.user_manager.create_user(user.email, 'password', user.first_name, user.last_name, user.birthdate, user.photo)
        #response = post_register(app, user.email, user.first_name, user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)

        self.user_manager.update_points(response.json()['body']['id'], 'increase')
        self.user_manager.update_points(response.json()['body']['id'], 'increase')

        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = user.id
        message.sender_id = user.id
        message.sender = user.email
        message.scheduled = True
        message.draft = False
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)
        title = get_page_id(app, '/mailbox/scheduled/' + str(m.id), 'page_title')
        self.assertEqual(title, 'Message')

        # ------ Test1: logged -----
        title = get_page_id(app, '/mailbox/scheduled', 'page_title')
        self.assertEqual(title, SCHEDULED)

         # ------ Test5: inbox with existing id and delete-----
        response = post_and_get_result_id(app,'/mailbox/scheduled/',{"delete":m.id},"page_title")
        self.assertEqual(response, SCHEDULED)

        # ------ GET: LOGOUT -----
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
        # ------ Test2: inbox with login -----
        title = get_page_id(app, '/mailbox/scheduled', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

    def get_mailbox(self):
        app = self.client
        #title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)
        # ------ Test1: logged -----
        title = get_page_id(app, '/mailbox', 'page_title')
        self.assertEqual(title, MAILBOX)


         #Create urls to test the searching of the message 
        BASE_URL = "http://localhost:5000/mailbox"
        TEST1 = BASE_URL + "?msg=prova&date=&user="

        resp=get_page_id(app,TEST1,"page_title")
        self.assertEqual(resp,"Search")


        # ------ GET: LOGOUT -----
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
        # ------ Test2: inbox with login -----
        title = get_page_id(app, '/mailbox', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
    """def test_play_lottery(self):
        response = post_and_get_result_id(self.client, '/playLottery', {'number': number}, html_id)"""

    def get_message(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)

        title = get_page_id(app, self.BASE_URL + '/message', 'page_title')
        self.assertEqual(title, MSG_CREATION_PAGE_TITLE)

        # ----- 3 POST: Write a message and save it
        # 2 messages to cover all cases
        response = post_message(app, user.email, 'hi', 
                '05/06/2022', '22:12', 'Draft', 'drafted')
        self.assertEqual(response, MSG_DRAFT)

        """response = post_message(app, user.email, 'hi', 
                '05/06/2022', '22:12', 'Draft', 'drafted')
        self.assertEqual(response, MSG_DRAFT)"""

         # ----- 3 POST: Write a message and schedule it
        # 2 messages to cover all cases
        response = post_message(app, user.email, 'hi', 
                '05/06/2022', '10:12', 'Schedule', 'scheduled')
        self.assertEqual(response, MSG_SCHEDULED) 

        """ response = post_message(app, 'example@example.com', 'hi', 
                '05/06/2022', '10:12', 'Schedule', 'scheduled')
        self.assertEqual(response, MSG_SCHEDULED) """
        
        # ----- 3 POST: Write an incorrect message (wrong date)
        response = post_message(app, user.email, 'hi', 
                '05/806/1998', '10:12', 'Draft', 'wrong_date')
        self.assertEqual(response, 'date: This field is required.')
        
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)


    def get_profile(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        username = post_login(self.client, user.email, 'password', 'username')
        self.assertEqual(username, user.first_name)

        title = get_page_id(app, self.BASE_URL + '/profile', 'page_title')
        self.assertEqual(title, PROFILE_PAGE_TITLE)
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

    def play_lottery(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        username = post_login(self.client, user.email, 'password', 'username')
        title = get_page_id(app, '/lottery', 'page_title')
        self.assertEqual(title, LOTTERY_PAGE_TITLE)

        error_number = post_lottery(app, 120, "error_number")
        self.assertEqual(error_number, LOTTERY_ERROR_NUMBER)
        # ------ 3 POST LOTTERY NUMBER SUCCEDED ------
        post_lottery(app, 22, "username")
        #self.assertEqual(username, username)

        title = get_page_id(app, '/lottery', 'page_title')
        self.assertEqual(title, LOTTERY_PAGE_TITLE)

        error_number = post_lottery(app, "a", "error_number")
        self.assertEqual(error_number, LOTTERY_ERROR_NUMBER)
        #post_lottery(app, "a", "username")
        #self.assertEqual(username, username)
        # ------ 4 POST WITH INCORRECT NUMBER ------
        error_number = post_lottery(app, 120, "error_number")
        self.assertEqual(error_number, LOTTERY_ERROR_NUMBER)

        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

    def edit_profile(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        post_login(self.client, user.email, 'password', 'username')
    
        # ------ 3 POST: USER UPDATES CORRECTLY HIS INFO (DATE OF BIRTH) ------
        response = post_update_profile(app, user.email, 'a', 
            'b', 'admin', '05/06/1998', 'profile_edited')
        self.assertEqual(response, UPDATE_DONE)

        # ------ 4 POST: USER DOESN'T UPDATE CORRECTLY HIS INFO (WRONG DATE OF BIRTH) ------
        response = post_update_profile(app, user.email, 'a', 
            'b', 'admin', '055/056/15998', 'wrong_date')
        self.assertEqual(response, WRONG_DATE)

        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        """
    # ------ 4 POST: USER DOESN'T UPDATE CORRECTLY HIS INFO (WRONG DATE OF BIRTH) ------
        response = post_update_profile(app, user.email, 'a', 
            'b', 'admin', '055/056/15998', 'wrong_date')
        self.assertEqual(response, WRONG_DATE)"""

    def report_user(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        post_login(self.client, user.email, 'password', 'username')
        title = get_page_id(app, '/users/report/' + user.email, 'page_title')
        # Client is logged, it is on the report page
        self.assertEqual(title, REPORT_PAGE_TITLE)

        # ------ 3 POST A REPORT, it works only before tests on update profile information ------
        post_report(app, user.email, "reason", 'username')

        # ------ 4 POST A REPORT WITH WRONG EMAIL ------
        error_email = post_report(app, "wrong_email@wrong.com", "reason", "wrong_email")
        self.assertEqual(error_email, WRONG_REPORT_EMAIL)


        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
    
    def check_delete(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        post_login(self.client, user.email, 'password', 'username')
         

        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = user.id
        message.sender_id = user.id
        message.sender = user.email
        message.scheduled = True
        message.draft = False
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)
        # ------ Test5: inbox with existing id and delete-----
        response = post_and_get_result_id(app,'/mailbox/inbox/',{"delete":m.id},"page_title")
        self.assertEqual(response, INBOX)
        
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
    def test_users(self):
        app = self.client
        user = generate_user()
        response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)
        post_login(self.client, user.email, 'password', 'username')
        response = app.get('/users')
        # Client is now logged, it can sees registered users
        self.assertEqual(response.status_code, 200)
        #Client tries to search the user admin
        response = get_page_id(app,'/users?search=admin','results')
        self.assertEqual(response, "You searched: admin")        
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
    def test_forward(self):
        app = self.client
        user = generate_user()
        response = self.user_manager.create_user(user.email, 'password', user.first_name, user.last_name, user.birthdate, user.photo)
        """response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)"""
        post_login(self.client, user.email, 'password', 'username')
        
        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = response.json()["body"]["id"]
        message.sender_id = response.json()["body"]["id"]
        message.sender = user.email
        message.scheduled = False
        message.read = 1
        message.draft = False
        message.sent=1
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)
        # ------ Test1: forward an existing message-----
        url="/mailbox/forward/"+str(m.id)
        response=get_page_id(app,url,"page_title")
           # Request the page
        # extract the html page from the response
        self.assertEqual(response, "Message")

        # ------ Test2: forward with wrong id-----
        url="/mailbox/forward/" + "-1"
        response=get_page_id(app,url,"page_title")
        self.assertEqual(response, MAILBOX)
        # ------ removing the created message-----
        response=post_and_get_result_id(app,'/mailbox/inbox/',{"delete":m.id},"page_title")
        self.assertEqual(response, INBOX)

        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
    """def test_draft_rm(self):
        app = self.client
        user = generate_user()
        response = self.user_manager.create_user(user.email, 'password', user.first_name, user.last_name, user.birthdate, user.photo)
        
        post_login(self.client, user.email, 'password', 'username')
        
        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = response.json()["body"]["id"]
        message.sender_id = response.json()["body"]["id"]
        message.sender = user.email
        message.scheduled = False
        message.read = 0
        message.draft = True
        message.sent = 0
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)

        from mib.views.message import draft_remove
       """

        

    def test_reply(self):
        app = self.client
        user = generate_user()
        response = self.user_manager.create_user(user.email, 'password', user.first_name, user.last_name, user.birthdate, user.photo)
        """response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)"""
        post_login(self.client, user.email, 'password', 'username')
        
        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email
        message.receiver_id = response.json()["body"]["id"]
        message.sender_id = response.json()["body"]["id"]
        message.sender = user.email
        message.scheduled = False
        message.read = 1
        message.draft = False
        message.sent=1
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao'
        m = self.message_manager.create_message(message)
        # ------ Test1: forward an existing message-----
        url="/mailbox/reply/"+str(m.id)
        response=get_page_id(app,url,"page_title")
           # Request the page
        # extract the html page from the response
        self.assertEqual(response, "Message")

        # ------ Test2: forward with wrong id-----
        url="/mailbox/reply/" + "-1"
        response=get_page_id(app,url,"page_title")
        self.assertEqual(response, MAILBOX)
        # ------ removing the created message-----
        response=post_and_get_result_id(app,'/mailbox/inbox/',{"delete":m.id},"page_title")
        self.assertEqual(response, INBOX)

        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)
        
        
    def test_validate_message(self):
        app = self.client
        user = generate_user()
        response = self.user_manager.create_user(user.email, 'password', user.first_name, user.last_name, user.birthdate, user.photo)
        r=self.user_manager.update_badwords(response.json()["body"]["id"],["evil","devil"])

        """response = post_register(app, user.email, user.first_name, 
            user.last_name, 'password', user.birthdate, user.photo, 'registration_done')
        self.assertEqual(response, REGISTRATION_DONE)"""
        post_login(self.client, user.email, 'password', 'username')
        message = Message()
        message.id = -1
        message.photo = ''
        message.receiver = user.email+", "+user.email+", "+"xd@xd.com"
        message.receiver_id = response.json()["body"]["id"]
        message.sender_id = response.json()["body"]["id"]
        message.sender = user.email
        message.scheduled = False
        message.read = 1
        message.draft = False
        message.sent=1
        message.bold = message.italic = message.underline = False
        message.timestamp = '03/03/2020 12:30'
        message.body = 'ciao evil'
        from mib.views.message import validate_message
        validate_message(message)
        title = get_page_id(app, self.BASE_URL + '/logout', 'page_title')
        self.assertEqual(title, LOGIN_PAGE_TITLE)

    def test_server_error(self):
        app = self.client

        response = app.get('/server_error', follow_redirects = True)
        assert response.status_code == 500