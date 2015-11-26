from base_handler import BaseHandler
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import urllib
import json
from config import config
from request_header import create_request_header
# Convert BSON cursors to json
from bson.json_util import dumps
# Validates python dictionaries - used to make sure incoming REST API requests are properly formatted
from voluptuous import Schema, Required

class ReminderHandler(BaseHandler):
  def initialize(self, reminders_collection):
    # Instance of ProductHandler has reference to reminders collection in MongoDB
    self.reminders = reminders_collection

  # Reminder_id defaults to none because this will handle getting all reminds for a specific user
  # Or detailed information about a specific reminder
  @gen.coroutine
  def get(self, reminder_id=None):
    # Returns up to 20 reminders for that user
    if reminder_id == None:
      all_user_reminders_cursor = self.reminders.find({"uber_id": self.current_user["uuid"]})
      user_reminders = yield all_user_reminders_cursor.to_list(length=20)
      self.write(dumps(user_reminders))
    # Return detailed information about a specific reminder
    else:
      pass

  @gen.coroutine
  def post(self):
    reminder_schema = Schema({
      Required("reminder_time"): int,
      Required("event"): {
        Required("time"): int,
        "name": str,
        "location": str,
        "latitude": float,
        "longitude": float,
        "product_id": string
      }  
    })
    reminder_request = json.loads(self.request.body)
    # Validate incoming request against schema
    try:
      reminder_schema(reminder_request)
    except:
      self.write("Invalid request!")

    reminder_data = yield self.create_reminder(self.current_user["tokens"]["access"], reminder_request)
    print(reminder_data)

  # HTTP helper that sends a request to the Uber API to make a new reminder
  @gen.coroutine
  def create_reminder(access_token, reminder_details):
    create_reminder_body = json.dumps(reminder_details)
    create_reminder_response = yield AsyncHTTPClient().fetch(
      config["endpoints"]["reminders"],
      method="POST",
      headers=create_request_header(access_token),
      body=create_reminder_body
    )
    raise gen.Return(json.loads(create_reminder_response.body))
