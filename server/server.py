import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClient
fro import config

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    http_client = HTTPClient()
    print("Making request...")
    response = http_client.fetch("https://bootstrap.pypa.io/get-pip.py")
    print("After request...")
    self.write(response.body)    

class AuthHandler(tornado.web.RequestHandler):
  def get(self):
    print(self.get_argument("code"))

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", tornado.web.RedirectHandler, dict(url=config["AUTH_REDIRECT"])),
    (r"/auth", AuthHandler)
  ])

if __name__ == "__main__":
  app = make_app()
  app.listen(8888)
  print(config["AUTH_REDIRECT"])
  print("Server listening on 8888")
  tornado.ioloop.IOLoop.current().start()

