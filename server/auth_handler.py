from config import config
from tornado.httpclient import AsyncHTTPClient
import tornado.web
from tornado import gen
import urllib
import json
from redis_conn import r
import jwt

class AuthHandler(tornado.web.RequestHandler):
  @gen.coroutine
  def get(self):
    # Get tokens
    token_data = yield request_token(self.get_argument("code"))
    # Get user profile information
    user_data = yield get_user(token_data["access_token"])
    # Store user profile information and tokens
    store_user(user_data, token_data)
    # Create JWT and store it in cookie
    create_session(user_data["uuid"], self)
    # Confirm success
    self.write("Successfully authenticated!")

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
  r.set(user_data["uuid"], json.dumps({
    "first_name": user_data["first_name"],
    "last_name": user_data["last_name"],
    "email": user_data["email"],
    "tokens": {
      "access": token_data["access_token"],
      "refresh": token_data["refresh_token"]
    }
  }))

def create_session(uuid, request_handler):
  # Create JWT that stores UUID
  user_jwt = jwt.encode({"uuid": uuid}, config["JWT_SECRET"], algorithm="HS256")
  request_handler.set_secure_cookie("JWT", user_jwt)