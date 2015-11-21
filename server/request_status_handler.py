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
    print("Websocket connection established!")
    pass

  def on_message(self, message):
    message = json.loads(message)
    if (message["type"] == "auth"):
      decoded_user_jwt = jwt.decode(message["message"], config["JWT_SECRET"], algorithms=["HS256"])
      # print(decoded_user_jwt)
      self.socket_connections[decoded_user_jwt["uuid"]] = self

  def on_close(self):
    print("Websocket connection closed!")
    # pass
