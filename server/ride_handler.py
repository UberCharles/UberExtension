from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config

@gen.coroutine
def request_ride(access_token, request_details):
  request_body = {
    "product_id": request_details["product_id"],
    "start_latitude": request_details["start_latitude"],
    "start_longitude": request_details["start_longitude"],
  }

  if "end_latitude" in request_details and "end_longitude" in request_details:
    request_body["end_latitude"] = request_details["end_latitude"]
    request_body["end_longitude"] = request_details["end_longitude"]

  request_body = json.dumps(request_body)
  request_header = {
    "Authorization": "BEARER " + access_token,
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  print(request_body);
  request_response = yield AsyncHTTPClient().fetch(
    config["endpoints"]["requests"], 
    method="POST", 
    body=request_body,
    headers=request_header)
  raise gen.Return(json.loads(request_response.body))

class RideHandler(BaseHandler):
  @gen.coroutine
  def post(self):
    request_details = json.loads(self.request.body)
    request_data = yield request_ride(self.current_user["tokens"]["access"], request_details)
    print(request_data)
    