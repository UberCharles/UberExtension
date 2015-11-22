from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config

@gen.coroutine
def request_price_estimate(access_token, coordinates):
  query_params = "?" + urllib.urlencode(coordinates)
  auth_header = {"Authorization": "BEARER " + access_token}
  products_response = yield AsyncHTTPClient().fetch(
    config["endpoints"]["price_estimates"] + query_params, 
    method="GET",
    headers=auth_header)
  raise gen.Return(json.loads(products_response.body))

class PriceEstimatesHandler(BaseHandler):
  @gen.coroutine
  def get(self):
    coordinates = {
      "start_latitude": self.get_argument("start_latitude"),
      "start_longitude": self.get_argument("start_longitude"),
      "end_latitude": self.get_argument("end_latitude"),
      "end_longitude": self.get_argument("end_longitude")
    }
    price_estimate_data = yield request_price_estimate(self.current_user["tokens"]["access"], coordinates)
    print(price_estimate_data)
    self.write(price_estimate_data)