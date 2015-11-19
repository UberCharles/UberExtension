from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config

@gen.coroutine
def request_products(access_token, coordinates):
  query_params = "?" + urllib.urlencode(coordinates)
  auth_header = {"Authorization": "BEARER " + access_token}
  products_response = yield AsyncHTTPClient().fetch(
    config["endpoints"]["products"] + query_params, 
    method="GET",
    headers=auth_header)
  raise gen.Return(json.loads(products_response.body))

class ProductHandler(BaseHandler):
  @gen.coroutine
  def get(self):
    coordinates = {
      "latitude": self.get_argument("latitude"),
      "longitude": self.get_argument("longitude")
    }
    products_data = yield request_products(self.current_user["tokens"]["access"], coordinates)
    self.write(products_data)