import tkinter as tk
import os
import math
from datetime import datetime
from tkinter import scrolledtext
from tkinter import *

window = tk.Tk()
window.configure(bg="white")

MAX_SPEED = 120
MIN_SPEED = 15

if not os.path.isdir("./logs"):
    try:
        os.mkdir("./logs")
    except OSError:
        print("Creation of logs directory failed.")
    else:
        print("Succesfully created logs directory.")

logfile = open("./logs/oceancruise_" +
               datetime.now().strftime("%m-%d-%y") + ".log", "a")
if os.path.getsize("./logs/oceancruise_" + datetime.now().strftime("%m-%d-%y") + ".log") > 0:
    logfile.write("\n")
logfile.write(
    "[" + datetime.now().strftime("%H:%M:%S") + "] Vehicle turned on.")
firstMsg = True
cruiseEnabled = False
currentSpeed = 0.0
setSpeed = 0
state = "Disabled"

actionLog = scrolledtext.ScrolledText(
    window, width=100, state=DISABLED, borderwidth=2, relief="groove")
actionLabel = Label(window, width=45, text="Actions Log",
                    font=("Arial", 15), pady=8, background="white")
stateLabel = Label(window, width=45, text="Current State: " +
                   state, font=("Arial", 15), background="white")
speedLabel = Label(window, width=45, text="Current Speed: " +
                   str(currentSpeed) + " MPH", font=("Arial", 15), background="white")

actionLabel.grid(column=0, row=0, columnspan=5)
actionLog.grid(column=0, row=1, columnspan=5, sticky=NSEW)
stateLabel.grid(column=0, row=2, columnspan=5, sticky=NSEW, pady=(12, 0))
speedLabel.grid(column=0, row=3, columnspan=5, sticky=NSEW, pady=12)

brakeBtn = Button(window, width=15, text="Apply Brake",
                  font=("Arial", 12), background="white")
accelBtn = Button(window, width=15, text="Apply Accelerator",
                  font=("Arial", 12), background="white")
enableBtn = Button(window, width=20, text="Enable Cruise Control",
                   font=("Arial", 12), background="white")
upBtn = Button(window, width=5, text="+", font=("Arial", 12),
               background="pale green", activebackground="lime green")
dwnBtn = Button(window, width=5, text="-", font=("Arial", 12),
                background="tomato", activebackground="red")

cpyLabel = Label(window, width=45, text="OceanCruise Simulation Interface - Developed by OceanByte, Spring 2020",
                 font=("Arial Bold", 10), background="Navy", fg="White")
cpyLabel.grid(column=0, row=5, columnspan=5, sticky=NSEW, pady=(32, 0))


def change_state(new_state):
    global state
    state = new_state
    stateLabel.configure(text="Current State: " + new_state)


def log_msg(msg):
    global firstMsg, logfile
    actionLog.configure(state='normal')
    if not firstMsg:
        actionLog.insert(tk.END, "\n")
    firstMsg = None
    timestamp = "[" + datetime.now().strftime("%H:%M:%S") + "] "
    actionLog.insert(tk.END, timestamp + msg)
    actionLog.configure(state='disabled')
    logfile.write("\n" + timestamp + msg)


def deaccelerate():
    if state == "Disabled":
        global currentSpeed
        if currentSpeed > 0:
            currentSpeed -= 0.05
        else:
            currentSpeed = 0
        speedLabel.configure(text="Current Speed: %.1f MPH" % currentSpeed)
        enableBtn.after(100, deaccelerate)


def update_speed(currentSpeed):
    global setSpeed, cruiseEnabled
    if cruiseEnabled:
        speedLabel.configure(text="Current Speed: %.1f MPH    Set Speed: %.1f MPH" % (
            currentSpeed, setSpeed))
    else:
        speedLabel.configure(text="Current Speed: %.1f MPH" % currentSpeed)


def cruise():
    global currentSpeed, cruiseEnabled
    if state == "Enabled":
        if currentSpeed < setSpeed:
            currentSpeed += 0.1
        elif currentSpeed > setSpeed:
            currentSpeed -= 0.05
        update_speed(currentSpeed)

    if cruiseEnabled:
        enableBtn.after(30, cruise)


def disable_cruise(msg):
    global cruiseEnabled, state
    cruiseEnabled = False
    change_state("Disabled")
    log_msg("Disabled cruise control for reason: " + msg)
    enableBtn.configure(text="Enable Cruise Control")
    deaccelerate()


def enable_cruise():
    global cruiseEnabled, setSpeed, currentSpeed, MIN_SPEED
    if state != "Braking":
        if currentSpeed < MIN_SPEED:
            log_msg("Could not enable cruise control, current speed (%.1f MPH) is less than the minimum of %d MPH." % (
                currentSpeed, MIN_SPEED))
            return
        cruiseEnabled = True
        if state != "Accelerating":
            change_state("Enabled")
        log_msg("Enabled cruise control, maintaining a speed of %.1f MPH." %
                currentSpeed)
        setSpeed = currentSpeed
        enableBtn.configure(text="Disable Cruise Control")
        cruise()
    else:
        log_msg("Could not enable cruise control, brake is applied.")


def toggle_cruise():
    global cruiseEnabled
    if cruiseEnabled:
        disable_cruise("disable button pressed")
    else:
        enable_cruise()


def accelerate():
    if state == "Accelerating":
        global currentSpeed, MAX_SPEED
        if currentSpeed < MAX_SPEED:
            currentSpeed += 0.1
        update_speed(currentSpeed)
        accelBtn.after(25, accelerate)


def brake():
    if state == "Braking":
        global currentSpeed
        if currentSpeed > 0:
            currentSpeed -= 0.25
        else:
            currentSpeed = 0
        update_speed(currentSpeed)
        brakeBtn.after(25, brake)


def toggle_accel():
    global state
    if state == "Braking":
        log_msg("Couldn't apply accelerator, brake is applied.")
        return
    if state != "Accelerating":
        change_state("Accelerating")
        accelBtn.configure(text="Release Accelerator")
        log_msg("Accelerator was applied.")
        accelerate()
    else:
        if cruiseEnabled:
            change_state("Enabled")
        else:
            change_state("Disabled")
            deaccelerate()
        accelBtn.configure(text="Apply Accelerator")
        log_msg("Accelerator was released.")


def toggle_brake():
    global state, cruiseEnabled

    if cruiseEnabled:
        disable_cruise("application of brake")

    if state != "Braking":
        if state == "Accelerating":
            toggle_accel()
        change_state("Braking")
        brakeBtn.configure(text="Release Brake")
        log_msg("Brake was applied.")
        brake()
    else:
        change_state("Disabled")
        brakeBtn.configure(text="Apply Brake")
        log_msg("Brake was released.")
        deaccelerate()


def increase_cruise():
    global setSpeed, cruiseEnabled, MAX_SPEED
    if cruiseEnabled:
        if setSpeed + 1 > MAX_SPEED:
            log_msg(
                "Couldn't increase cruising speed, attempting to increase speed above maximum speed of %d MPH." % MAX_SPEED)
        else:
            setSpeed = math.ceil(setSpeed + 1)
            log_msg("Cruising speed increased to %.1f MPH." % setSpeed)

    else:
        log_msg("Couldn't increase cruising speed, cruise control is not enabled.")


def decrease_cruise():
    global setSpeed, cruiseEnabled, MIN_SPEED
    if cruiseEnabled:
        if setSpeed - 1 < MIN_SPEED:
            log_msg(
                "Couldn't decrease cruising speed, attempting to decrease speed below minimum speed of %d MPH." % MIN_SPEED)
        else:
            setSpeed = math.floor(setSpeed - 1)
            log_msg("Cruising speed decreased to %.1f MPH." % setSpeed)
    else:
        log_msg("Couldn't decrease cruising speed, cruise control is not enabled.")


brakeBtn.configure(command=toggle_brake)
accelBtn.configure(command=toggle_accel)
enableBtn.configure(command=toggle_cruise)
upBtn.configure(command=increase_cruise)
dwnBtn.configure(command=decrease_cruise)

brakeBtn.grid(column=0, row=4)
accelBtn.grid(column=1, row=4)
enableBtn.grid(column=2, row=4)
upBtn.grid(column=3, row=4)
dwnBtn.grid(column=4, row=4)

window.title("OceanCruise Interface")
window.mainloop()
if cruiseEnabled:
    logfile.write("\n[" + datetime.now().strftime("%H:%M:%S") + "] EMERGENCY: Executed emergency shutoff procedure, power was unexpectedly lost.")
logfile.write(
    "\n[" + datetime.now().strftime("%H:%M:%S") + "] Vehicle turned off.")
