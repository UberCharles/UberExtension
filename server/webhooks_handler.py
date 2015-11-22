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
        request_details = yield RideHandler.get_request(user_access_token,event_data["meta"]["resource_id"])
        event_message["details"] = {
            "driver": request_details["driver"],
            "eta": request_details["eta"],
            "vehicle": request_details["vehicle"] 
        }
    user_socket.write_message(json.dumps(event_message))
    