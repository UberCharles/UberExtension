from config import config
from tornado.httpclient import AsyncHTTPClient
import tornado.web
from tornado import gen
import urllib

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
  raise gen.Return(token_response.body)
  
class AuthHandler(tornado.web.RequestHandler):
  @gen.coroutine
  def get(self):
    token_data = yield request_token(self.get_argument("code"))
    print(token_data)