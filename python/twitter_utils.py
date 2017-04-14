import oauth2
import constants
import urllib.parse as urlparse


consumer = oauth2.Consumer(constants.CONSUMER_KEY, constants.CONSUMER_SECRET)

# it makes a bit more sense to have this in twitter_utils vs user.py
def get_request_token():
    client = oauth2.Client(consumer)
    # first input is the website to request token urls, and the 2nd input is a verb
    # two things are returned, response and content
    response, content = client.request(constants.REQUEST_TOKEN_URL, 'POST')
    if response.status != 200:
        print("An error occured getting the request token from Twitter!")

    # get the request token pasing the query string returned
    return dict(urlparse.parse_qsl(content.decode('utf-8')))

def get_oauth_verifier(request_token):
    # ask the user to authorize the app and supply PIN code
    print("Go to the following site in your browser: ")
    # access token request format. found request_token['oauth_token'] with the python debugger
    print("{}?oauth_token={}".format(constants.AUTHORIZATION_URL, request_token['oauth_token']))

    return input('What is the PIN? ')

def get_access_token(request_token, oauth_verifier):
    # combines the oauth request token, and its secret to create an oauth verifier
    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)

    client = oauth2.Client(consumer, token)

    # now we can use this client^ to get the access token!!! asks twitter for access token, because
    # we verified our request token
    response, content = client.request(constants.ACCESS_TOKEN_URL, 'POST')
    # now we parse the query string and turn it into a dict
    return dict(urlparse.parse_qsl(content.decode('utf-8')))