from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

load_dotenv()

kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))

print ("Login URL:", kite.login_url())

request_token = input("Enter the request token: ")

data = kite.generate_session(
    request_token=request_token,
    api_secret=os.getenv("KITE_API_SECRET")
)

kite.set_access_token(data["access_token"])
print("Authentication successful. Access token set.")

print (f"Access Token: {data['access_token']}")