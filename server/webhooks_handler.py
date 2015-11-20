from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config

class WebhooksHandler(BaseHandler):
  @gen.coroutine
  def post(self):
    print(self.request.body)
    