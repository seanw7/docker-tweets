from database import Database, CursorFromConnectionFromPool
from user import User
from twitter_utils import get_request_token, get_oauth_verifier, get_access_token
import psycopg2

# first we need to create a consumer, which is an object that represents our
# application and allows twitter api to recognize its our app.
# If the users' email is found in the Database. We can use their auth token info.
loginCheck = input("What is your email? ")
searchText = input('What do you want to search for(spaces should be %20)?: ')
#searchText='learn%20python+filter:images'
Database.initialise(database='postgres', user='postgres', password='postgres', host='db')

user = User.load_from_db_by_email(loginCheck)

if not user:
    print("Couldn't find user with that email... Lets create a User... \n")
    request_token = get_request_token()

    oauth_verifier = get_oauth_verifier(request_token)

    access_token = get_access_token(request_token, oauth_verifier)
    print(access_token)
    # now we can use this Access token to create requests to twitter!

    #uEmail = input("Enter your email: ")
    uFirstName = input("Enter your first name: ")
    uLastName = input("Enter your last name: ")
    user= User(loginCheck, uFirstName, uLastName, access_token['oauth_token'], access_token['oauth_token_secret'], None)
    user.save_to_db()  ## If user is created... add user to DB

print("Found user: <{}>, creating authentication token... \n\n--Twitter posts--\n".format(user.email))





# this allows us to decode the returned query
# print(content.decode('utf-8')) #  originally was this cmd
# Twitter returns JSON files to your query requests. and it is returned as a string, we must convert it into a dict
# to do this we import json @ the top and then make this json.loads(content...)
tweets = user.twitter_request('https://api.twitter.com/1.1/search/tweets.json?q={}'.format(searchText))

for tweet in tweets['statuses']:
    print(tweet['text'])
    print('https://www.twitter.com/' + tweet['user']['screen_name'] + '\n')
    # to improve on this program you can start storing authorized tokens so that you dont have to authorize the app every time
