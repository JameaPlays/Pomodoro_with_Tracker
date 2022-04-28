from tkinter import *
import math
import requests
from datetime import datetime as dt
import os
from dotenv import load_dotenv
load_dotenv()

reps = 0
timer = None
USERNAME = os.environ["PIXELA_USERNAME"]
TOKEN = os.environ["PIXELA_TOKEN"]
GRAPH_ID = "pythonstudy"
PIXELA_ENDPOINT = "https://pixe.la/v1/users"
HEADERS = {"X-USER-TOKEN": TOKEN}
study_time = 0
session_start_time = None

today_date = dt.now().strftime("%Y%m%d")
print(today_date)

pixel_config = {
            "date": '20220321',
            "quantity": str(48.625)
        }

response = requests.post(
            url=f"{PIXELA_ENDPOINT}/{USERNAME}/graphs/{GRAPH_ID}",
            json=pixel_config,
            headers=HEADERS
        )
print(response.text)
