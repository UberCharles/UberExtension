from base_handler import BaseHandler

class ProductHandler(BaseHandler):
  @gen.coroutine
  def get(self):
    latitude = self.get_argument("latitude")
    longitude = self.get_argument("longitude")
    print(latitude)
    print(longitude)