import tornado.ioloop
import tornado.web
import urllib
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClient
from config import config

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    http_client = HTTPClient()
    print("Making request...")
    response = http_client.fetch("https://bootstrap.pypa.io/get-pip.py")
    print("After request...")
    self.write(response.body)    

class AuthHandler(tornado.web.RequestHandler):
  @gen.coroutine
  def get(self):
    auth_code = self.get_argument("code")
    request_data = urllib.urlencode({
      "client_secret": config["SECRET"],
      "client_id": config["CLIENT_ID"],
      "grant_type": "authorization_code",
      "redirect_uri": config["REDIRECT_URI"],
      "code": auth_code
    })
    print(request_data)
    # Don't need to yield because we can fire and forget
    response = yield AsyncHTTPClient().fetch(config["TOKEN_URI"], method="POST", body=request_data)
    print(response.body)

class TokenHandler(tornado.web.RequestHandler):
  def get(self):
    print("Token route called")


def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", tornado.web.RedirectHandler, dict(url=config["AUTH_REDIRECT"])),
    (r"/auth", AuthHandler),
    (r"/token", TokenHandler)
  ])

if __name__ == "__main__":
  app = make_app()
  app.listen(8888)
  print("Server listening on 8888")
  tornado.ioloop.IOLoop.current().start()

