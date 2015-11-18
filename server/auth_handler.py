from config import config
from tornado.httpclient import AsyncHTTPClient
import tornado.web
from tornado import gen
import urllib
import json
from redis_conn import r

class AuthHandler(tornado.web.RequestHandler):
  @gen.coroutine
  def get(self):
    # Get tokens
    token_data = yield request_token(self.get_argument("code"))
    # Get user profile information
    user_data = yield get_user(token_data["access_token"])
    # Store user profile information and tokens
    store_user(user_data, token_data)
    # TODO: Send client JWT for further requests

# Requests access / refresh token
@gen.coroutine
def request_token(auth_code):
  request_data = urllib.urlencode({
    "client_secret": config["SECRET"],
    "client_id": config["CLIENT_ID"],
    "grant_type": "authorization_code",
    "redirect_uri": config["REDIRECT_URI"],
    "code": auth_code
  })
  token_response = yield AsyncHTTPClient().fetch(config["TOKEN_URI"], method="POST", body=request_data)
  raise gen.Return(json.loads(token_response.body))

# Gets user profile information
@gen.coroutine
def get_user(access_token):
  auth_header = {"Authorization": "BEARER " + access_token}
  user_response = yield AsyncHTTPClient().fetch(
    config["endpoints"]["profile"], 
    method="GET", 
    headers=auth_header)
  raise gen.Return(json.loads(user_response.body))

# Store user
def store_user(user_data, token_data):
  r.set(user_data["uuid"], {
    "first_name": user_data["first_name"],
    "last_name": user_data["last_name"],
    "email": user_data["email"],
    "tokens": {
      "access": token_data["access_token"],
      "refresh": token_data["refresh_token"]
    }
  })