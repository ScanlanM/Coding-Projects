import requests
from dotenv import load_dotenv
import os
from json import dumps

class Carrier:
    def __init__(self):
        self.carrier_prefix = "CARRIER"
        self.auth_path = "/oauth/token"
        self.auth_token = ""
        self.environment = ""
        self.base_url = ""
        self.auth_url = ""
        self.track_url = ""
        self.track_path = ""
        
    def authentication(self):
        self.get_creds()
        # call authentication API with credentials to return auth token like value for API requests.
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data=f"grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}"
        print(data)
        r = requests.post(self.auth_url,data=data,headers=headers)
        print(r)
        print(r.text)
        resp = r.json()
        self.auth_token = f"Bearer {resp['access_token']}"
        return self.auth_token
    
    def track_with_tracking_number(self,tracking_request_body):
        headers = {"X-locale":"en_US",
                   'Content-type': 'application/json',
                   "Authorization":self.auth_token}

        print(headers)
        print(tracking_request_body)
        tracking_request_body=dumps(tracking_request_body)
        r = requests.post(self.track_url, 
                          data=tracking_request_body, 
                          headers=headers)
        print(r.text)
        return r
    
    def auth_handler(self,r):
        # TODO normalize auth response if needed else return r
        return r
    
    def track_handler(self, r):
        # TODO normalize tracking response if needed else return r
        return r
    
    def build_req_url(self,path):
        req_url = f"{self.base_url}{path}"
        return req_url
    
    def get_creds(self):
        load_dotenv()
        self.api_key = os.environ.get(f"{self.carrier_prefix}_API_KEY")
        self.api_secret = os.environ.get(f"{self.carrier_prefix}_API_SECRET")
        pass
