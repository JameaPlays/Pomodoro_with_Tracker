from tkinter import *
import math
import requests
from datetime import datetime as dt
import os
from dotenv import load_dotenv
load_dotenv()

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
reps = 0
timer = None
USERNAME = os.environ["PIXELA_USERNAME"]
TOKEN = os.environ["PIXELA_TOKEN"]
GRAPH_ID = "pythonstudy"
PIXELA_ENDPOINT = "https://pixe.la/v1/users"
HEADERS = {"X-USER-TOKEN": TOKEN}
study_time = 0
session_start_time = None


# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    global reps, study_time
    window.after_cancel(timer)
    study_time -= WORK_MIN
    # Add last study session time to study time if it was reset midway through a study session
    if reps % 2 != 0:
        session_close_time = dt.now()
        last_rep_minutes = (session_close_time - session_start_time).total_seconds() / 60
        study_time += last_rep_minutes
    title_label.config(text="Timer")
    canvas.itemconfig(timer_text, text="00:00")
    check_marks.config(text="")
    reps = 0


# ---------------------------- TIMER MECHANISM ------------------------------- # 
def start_timer():
    global reps, study_time, session_start_time, session_close_time
    reps += 1
    work_secs = WORK_MIN * 60
    short_break_secs = SHORT_BREAK_MIN * 60
    long_break_secs = LONG_BREAK_MIN * 60
    if reps % 8 == 0:
        count_down(long_break_secs)
        title_label.config(text="Break", fg=RED)
    elif reps % 2 == 0:
        count_down(short_break_secs)
        title_label.config(text="Break", fg=PINK)
    else:
        session_start_time = dt.now()
        count_down(work_secs)
        title_label.config(text="Work", fg=GREEN)


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 
def count_down(count):
    count_min = math.floor(count / 60)
    count_sec = int(count % 60)
    if count_sec <= 9:
        count_sec = f"0{count_sec}"
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)
    else:
        global reps, study_time, WORK_MIN
        if reps % 2 != 0:
            study_time += WORK_MIN
        start_timer()
        marks = ""
        for _ in range(math.floor(reps/2)):
            marks += "✓"
        check_marks.config(text=marks)


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Pomodoro")
window.config(padx=50, pady=25, bg=YELLOW)

canvas = Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = PhotoImage(file="tomato.png")
canvas.create_image(100, 112, image=tomato_img)
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 25, "bold"))
canvas.grid(column=1, row=1, padx=20)

# Timer title Label
title_label = Label(text="Timer", font=(FONT_NAME, 50, "bold"), fg=GREEN, bg=YELLOW)
title_label.grid(column=1, row=0)

# Start button
start = Button(text="Start", font=(FONT_NAME, 15), highlightthickness=0, command=start_timer)
start.grid(column=0, row=2)

# Reset button
reset = Button(text="Reset", font=(FONT_NAME, 15), command=reset_timer)
reset.grid(column=2, row=2)

# Check mark label
check_marks = Label(font=(FONT_NAME, 15, "bold"), fg=GREEN, bg=YELLOW)
check_marks.grid(column=1, row=3)

window.mainloop()
# Add last study session time to study time if timer was closed midway through a study session
if reps % 2 != 0:
    session_close_time = dt.now()
    last_rep_minutes = (session_close_time - session_start_time).total_seconds() / 60
    study_time += last_rep_minutes

if study_time > 0:
    # Posting / Updating pixel in pixela graph
    today_date = dt.now().strftime("%Y%m%d")
    # Get existing study time for today
    try:
        response = requests.get(
            url=f"{PIXELA_ENDPOINT}/{USERNAME}/graphs/{GRAPH_ID}/{today_date}",
            headers=HEADERS
        )
        current_graph_value = float(response.json()["quantity"])
    # If first study session for the day, post current session's study time
    except KeyError:
        pixel_config = {
            "date": today_date,
            "quantity": str(study_time)
        }
        response = requests.post(
            url=f"{PIXELA_ENDPOINT}/{USERNAME}/graphs/{GRAPH_ID}",
            json=pixel_config,
            headers=HEADERS
        )
        print(response.text)
    # If not first study session, add existing study time + current session study time and update pixel
    else:
        study_time += current_graph_value
        pixel_config = {
            "quantity": str(study_time)
        }
        response = requests.put(
            url=f"{PIXELA_ENDPOINT}/{USERNAME}/graphs/{GRAPH_ID}/{today_date}",
            json=pixel_config,
            headers=HEADERS
        )
        print(response.text)

# Delete existing pixel (for testing purposes)
# response = requests.delete(
#         url=f"{PIXELA_ENDPOINT}/{USERNAME}/graphs/{GRAPH_ID}/{today_date}",
#         headers=HEADERS
#     )
# print(response.text)
