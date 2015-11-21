from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config
from request_status_handler import RequestStatusHandler
from redis_conn import r

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
    user_socket.write_message(json.dumps({"type": event_data["event_type"], "status": event_data["meta"]["status"]}))
    