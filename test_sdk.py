import os
from dotenv import load_dotenv
from bookprintapi import Client
load_dotenv()
client = Client()
balance = client.credits.get_balance()
print(f"충전금 잔액: {balance}")
