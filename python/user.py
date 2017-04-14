from database import CursorFromConnectionFromPool
import oauth2
from twitter_utils import consumer
import json



class User():
    def __init__(self, email, first_name, last_name, oauth_token, oauth_token_secret, id):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.id = id

        # REPR method allows you to print an object, it must return a string
    def __repr__(self):
        return "<User: {}>".format(self.email)

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            # next we use the cursor. It is a tool that lets you retrieve data and read it row by row
            # Running some code... inserting values into users table. Remember that ID is self-incrementing.
            cursor.execute('INSERT INTO users (email, first_name, last_name, oauth_token, oauth_token_secret) '
                           'VALUES (%s, %s, %s, %s, %s)',
                           (self.email, self.first_name, self.last_name, self.oauth_token, self.oauth_token_secret,))

    @classmethod  # This method doesnt access the currently bound object. 'cls' stand for currently bound class
    def load_from_db_by_email(cls, email):
        with CursorFromConnectionFromPool() as cursor:
            # undeclared variable in a string, email var at the top
            cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
            # we have to define a tuple here because it thinks the parenthesis around email aren't needed.
            # we do that by adding a ',' comma in behind email like this (email,) this lets python know its a tuple
            # cursor.fetchone() should get us the first user with that email.
            user_data = cursor.fetchone()
            # this is how you return the row from postgres. you can change the index order of returned items like this
            if user_data:
                return cls(email=user_data[1], first_name=user_data[2], last_name=user_data[3],
                           oauth_token=user_data[4], oauth_token_secret=user_data[5], id=user_data[0])

    @classmethod
    def load_pw_by_email(cls, email):
        with CursorFromConnectionFromPool() as cursor:
            # undeclared variable in a string, email var at the top
            cursor.execute('SELECT oauth_token, oauth_token_secret from users WHERE email=%s', (email,))
            # we have to define a tuple here because it thinks the parenthesis around email aren't needed.
            # we do that by adding a ',' comma in behind email like this (email,) this lets python know its a tuple
            # cursor.fetchone() should get us the first user with that email.
            user_data = cursor.fetchone()
            if user_data:
                # this should create an authorization token...
                return cls(oauth_token=user_data[0], oauth_token_secret=user_data[1])

    def twitter_request(self, uri, verb='GET'):
        authorized_token = oauth2.Token(self.oauth_token, self.oauth_token_secret)
        authorized_client = oauth2.Client(consumer, authorized_token)

        #making twitter api calls!
        response, content = authorized_client.request(uri, verb)
        if response.status != 200:
            prnt("An error ocurred when searching!")

        return json.loads(content.decode('utf-8'))


