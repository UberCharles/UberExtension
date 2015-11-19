from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config

# @gen.coroutine
# def request_ride(access_token):

class ride_handler(BaseHandler):
  @gen.coroutine
  def post(self):
    request_details = json.loads(self.request.body)
    print(request_details)