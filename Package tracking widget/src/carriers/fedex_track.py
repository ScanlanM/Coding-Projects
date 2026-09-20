from carrier import Carrier
from dotenv import load_dotenv
import os

class Fedex(Carrier):
    def __init__(self):
        self.carrier_prefix = "FEDEX"
        self.base_url = "https://apis.fedex.com"
        self.track_path = "/track/v1/trackingnumbers"
        self.auth_path = "/oauth/token"
        self.auth_url = self.build_req_url(self.auth_path)
        self.track_url = self.build_req_url(self.track_path)
        self.auth_token = self.authentication()

    def track(self, tracking_number,detailedScans="false"):
        tracking_request_body = {
            "includeDetailedScans":detailedScans,
                "trackingInfo":[
                    {
                    "trackingNumberInfo":{
                        "trackingNumber":tracking_number
                        }
                    }
                ]
            }
        
        r = self.track_with_tracking_number(tracking_request_body)
        print(r.text)
        return r

fedex = Fedex()
load_dotenv()
PACK_TO_TRACK=os.environ.get("PACK_TO_TRACK")
fedex.track(PACK_TO_TRACK)

