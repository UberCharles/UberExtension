import tornado.websocket
import json
import jwt
from config import config

class RequestStatusHandler(tornado.websocket.WebSocketHandler):

  socket_connections = {}

  # Allows CORS
  def check_origin(self, origin):
    return True

  def open(self):
    self.user_UUID = None
    print("Websocket connection established!")

  def on_message(self, message):
    message = json.loads(message)
    # Store connection in dictionary with UUID as key so messages can be sent later
    if (message["type"] == "auth"):
      decoded_user_jwt = jwt.decode(message["message"], config["JWT_SECRET"], algorithms=["HS256"])
      self.socket_connections[decoded_user_jwt["uuid"]] = self
      # Also store UUID on instance so it can be removed from dictionary when connection closes
      self.user_UUID = decoded_user_jwt["uuid"]

  def on_close(self):
    # Remove key if exists, otherwise return default (None) -- Won't raise key-error
    self.socket_connections.pop(self.user_UUID, None)
    print("Websocket connection closed!")