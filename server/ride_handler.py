from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config
from redis_conn import r
from request_header import create_request_header

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
    # Store the UUID of the user who the active request belongs to
    r.set("requests:" + request_data["request_id"], self.current_user["uuid"])
    self.write(request_data)

  @gen.coroutine
  def get(self, request_id):
    request_data = yield self.get_request(self.current_user["tokens"]["access"], request_id)
    print(request_data)

  @gen.coroutine
  def delete(self, request_id):
    delete_request = yield self.delete_request(self.curent_user["tokens"]["access"], request_id)
    if delete_request == 204:
      self.set_status(204)
      self.write("Success!")
    else:
      self.set_status(400)
      self.write("Failure!")

  @staticmethod
  @gen.coroutine
  def get_request(access_token, request_id):
    request_header = create_request_header(access_token)
    request_response = yield AsyncHTTPClient().fetch(
      config["endpoints"]["requests"] + "/" + request_id,
      method="GET",
      headers=request_header)
    raise gen.Return(json.loads(request_response.body))

  @staticmethod
  @gen.coroutine
  def delete_request(access_token, request_id):
    request_header = create_request_header(access_token)
    delete_request_response = yield AsyncHTTPClient().fetch(
      config["endpoints"]["requests"] + "/" + request_id,
      method="DELETE",
      headers=request_header)
    raise gen.Return(request_response.code)

