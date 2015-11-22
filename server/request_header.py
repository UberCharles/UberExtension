def create_request_header(access_token):
  return {
    "Authorization": "BEARER " + access_token,
    "Accept": "application/json",
    "Content-Type": "application/json"
  }