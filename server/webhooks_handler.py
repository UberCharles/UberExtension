from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config
from request_status_handler import RequestStatusHandler
from redis_conn import r
from ride_handler import RideHandler

class WebhooksHandler(BaseHandler):
  @gen.coroutine
  def post(self):
    event_data = json.loads(self.request.body)
    # print(self.request.body)
    # print(RequestStatusHandler.socket_connections)
    # Look up UUID of user based on request_id of webhook event
    user_uuid = r.get("requests:" + event_data["meta"]["resource_id"])
    # Get the websocket connection that corresponds to that user UUID
    user_socket = RequestStatusHandler.socket_connections[user_uuid]
    event_message = {"type": event_data["event_type"], "status": event_data["meta"]["status"]}
    # If status is "accepted" then obtain request details to send to client
    if event_data["meta"]["status"] == "accepted":
        user_access_token = json.loads(r.get("users:" + user_uuid))["tokens"]["access"]
        request_details = yield RideHandler.get_request(user_access_token, event_data["meta"]["resource_id"])
        print("Request details:")
        print(request_details)
        # Details will contain info about driver and vehicle and eta
        event_message["details"] = {
            # Driver schema 
            "driver": {
                "name": request_details["driver"]["name"],
                "rating": request_details["driver"]["rating"],
                "phone_number": request_details["driver"]["phone_number"],
                "picture_url": request_details["driver"]["picture_url"]
            },
            "eta": request_details["eta"],
            # Vehicle schema
            "vehicle": {
                "make": request_details["vehicle"]["make"],
                "model": request_details["vehicle"]["model"],
                "license_plate": request_details["vehicle"]["license_plate"],
                "picture_url": request_details["vehicle"]["picture_url"]
            }
        }
    user_socket.write_message(json.dumps(event_message))
    