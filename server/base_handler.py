import jwt
import tornado.web
from redis_conn import r
from config import config
import json

class BaseHandler(tornado.web.RequestHandler):
  # Allows CORS
  def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

  def get_current_user(self):
    # Check if cookie exists
    user_jwt = self.get_cookie("JWT")
    print(user_jwt)
    if user_jwt != None:
      # If it does, decode it
      decoded_user_jwt = jwt.decode(user_jwt, config["JWT_SECRET"], algorithms=["HS256"])
      # Return users info from Redis
      return json.loads(r.get("users:" + decoded_user_jwt["uuid"]))
    else:
      # If no cookie, no user exists
      return None