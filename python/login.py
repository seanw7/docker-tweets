import constants
import oauth2
import urllib.parse as urlparse
import json
from database import Database, CursorFromConnectionFromPool
from user import User
import psycopg2

# first we need to create a consumer, which is an object that represents our
# application and allows twitter api to recognize its our app.
consumer = oauth2.Consumer(constants.CONSUMER_KEY, constants.CONSUMER_SECRET)
client = oauth2.Client(consumer)

#searchText = input("What do you want to search for(spaces should be %20)?: ")
#searchText='learn%20python+filter:images'   # 192.168.99.101 devenv ip
Database.initialise(database='postgres', user='postgres', password='postgres', host='db')
searchText = "technologent"
loginCheck = input("What is your email? ")
#try:
user = User.load_from_db_by_email(loginCheck)
# except Exception:
#     with CursorFromConnectionFromPool() as cursor:
#         cursor.execute("CREATE TABLE public.users(id serial NOT NULL, email character varying(255), first_name character varying(255), last_name character varying(255), oauth_token character varying(255), oauth_token_secret character varying(255), CONSTRAINT users_pkey PRIMARY KEY (id)) WITH (OIDS = FALSE) TABLESPACE pg_default; ALTER TABLE public.users OWNER to postgres")
#         print("Added table to DB.. try again...")
#         user = input("Enter Email again:")

if not user:  ##  If the users' email is found in the Database. We can use their auth token info.
    print("Couldn't find user with that email... Lets create a User... \n")
    # first input is the website to request token urls, and the 2nd input is a verb
    # two things are returned, response and content
    response, content = client.request(constants.REQUEST_TOKEN_URL, 'POST')
    if response.status != 200:
        print("An error occured getting the request token from Twitter!")

    # get the request token pasing the query string returned
    request_token = dict(urlparse.parse_qsl(content.decode('utf-8')))

    # ask the user to authorize the app and supply PIN code
    print("Go to the following site in your browser: ")

    # access token request format. found request_token['oauth_token'] with the python debugger
    print("{}?oauth_token={}".format(constants.AUTHORIZATION_URL, request_token['oauth_token']))


    oauth_verifier = input('What is the PIN? ')

    # this is a token object, combines the oauth request token, and its secret to create an oauth verifier
    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(consumer, token)

    # now we can use this client^ to get the access token!!! asks twitter for access token, because
    # we verified our request token
    response, content = client.request(constants.ACCESS_TOKEN_URL, 'POST')
    # now we parse the query string and turn it into a dict
    access_token = dict(urlparse.parse_qsl(content.decode('utf-8')))

    # now we can use this Access token to create requests to twitter!
    print(access_token)

    uEmail = input("Enter your email: ")
    uFirstName = input("Enter your first name: ")
    uLastName = input("Enter your last name: ")
    user= User(uEmail, uFirstName, uLastName, access_token['oauth_token'], access_token['oauth_token_secret'], None)
    user.save_to_db()  ## If user is created... add user to DB

print("Found user: <{}>, creating authentication token... \n\n--Twitter posts--\n".format(user.email))
    # create an 'authenticated_token' token object and use that to perform Twitter API calls on behalf of the user
authorized_token = oauth2.Token(user.oauth_token, user.oauth_token_secret)

authorized_client = oauth2.Client(consumer, authorized_token)

# Make Twitter API calls! the query string brgins with '?q=' so put your request after that... dont forget the verb!
response, content = authorized_client.request(
    'https://api.twitter.com/1.1/search/tweets.json?q={}'.format(searchText), 'GET')
if response.status != 200:
    print("An error occurred while searching!")

# this allows us to decode the returned query
# print(content.decode('utf-8')) #  originally was this cmd
# Twitter returns JSON files to your query requests. and it is returned as a string, we must convert it into a dict
# to do this we import json @ the top and then make this json.loads(content...)
tweets = json.loads(content.decode('utf-8'))

for tweet in tweets['statuses']:
    print(tweet['text'])
    print('https://www.twitter.com/' + tweet['user']['screen_name'] + '\n')
    # to improve on this program you can start storing authorized tokens so that you dont have to authorize the app every time
