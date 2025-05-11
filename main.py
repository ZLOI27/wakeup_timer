#!/usr/bin/env python3

import socket
import os
import time
import sys
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By


WEBSITE = "https://www.rbc.ru"
TIME_OF_NEWS = 200  # Seconds
TON_BEFORE_RISE_VOL = 600  # Time of news before rise volume(seconds)
TIME_WAKEUP = (5, 30)


def main() -> None:
    """
    This programm set timer to wakeup system from suspend and opens
    a browser and website with news.
    """
    time_wakeup = get_time_wakeup(TIME_WAKEUP)
    date_wakeup = get_date_wakeup(time_wakeup)
    date_time_wakeup = f'{time_wakeup[0]}:{time_wakeup[1]}'  # get_date_time_rtc(time, date)
    os.system(f"sudo rtcwake -u --date {date_time_wakeup}")
    if ask_suspend():
        os.system("sudo systemctl suspend")
    time.sleep(5)
    while True:
        if check_internet():
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 20%")
            driver = webdriver.Firefox()
            driver.get(WEBSITE)
            driver.maximize_window()
            time.sleep(2)
            fullscreen_on(driver)
            time.sleep(20)
            site_sound_on(driver)
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 50%")
            time.sleep(TON_BEFORE_RISE_VOL)
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 75%")
            time.sleep(TIME_OF_NEWS)
            driver.quit()
            os.system("systemctl suspend")
            break
        else:
            print("Disable internet connection")
            time.sleep(2)


def check_internet(host="8.8.8.8", port=53, timeout=3) -> bool:
    """Testing internet conection with DNS-server Google (8.8.8.8)."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def fullscreen_on(driver: object) -> None:
    """Fullscreen videostream on the website."""
    fullscreen_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__fullscreen"
    )
    fullscreen_btn.click()
    fullscreen_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__fullscreen"
    )
    fullscreen_btn.click()


def site_sound_on(driver: object) -> None:
    """Turn on the sound on the website."""
    volume_btn = driver.find_element(
            By.CLASS_NAME, "video-player__controls__volume"
    )
    volume_btn.click()


def get_time_wakeup(TIME_WAKEUP: tuple) -> tuple:
    """
    This function asks you to enter the time in the format hh*mm or
    h*mm (* is any character, not digit) and processes it. If no time
    is entered, then the standart time is taken from the constant.
    """
    hours = ''
    minutes = ''
    try:
        while True:
            time_str = input("Enter time hh:mm : ").strip()
            if len(time_str) == 0:
                return TIME_WAKEUP
            for char in time_str:
                if char.isdigit():
                    minutes += char
                else:
                    hours = minutes
                    minutes = ''
            if hours == '' or minutes == '':
                print("Incorrect input, please try again...")
                continue
            if 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59:
                return (int(hours), int(minutes))
            else:
                print("Incorrect input, please try again...")
                continue
    except EOFError:
        print("Input interrupted. EXIT.")
        sys.exit()


def get_date_wakeup(time_wakeup: tuple) -> tuple:
    """
    This function asks you to enter the date in the format dd*mm or
    d*m (* is any character, not digit) and processes it. If no date
    is entered, then the timer is set for today or tomorrow.
    """
    day = ''
    month = ''
    try:
        while True:
            date_str = input("Enter date dd:mm : ").strip()
            if len(date_str) == 0:
                return today_or_tomorrow(time_wakeup)
            for char in date_str:
                if char.isdigit():
                    month += char
                else:
                    day = month
                    month = ''
            if day == '' or month == '':
                print("Incorrect input, please try again...")
                continue
            if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
                return (int(day), int(month))
            else:
                print("Incorrect input, please try again...")
                continue
    except EOFError:
        print("Input interrupted. EXIT.")
        sys.exit()


def today_or_tomorrow(time_wakeup: tuple) -> tuple:
    """
    This function checks the entered time, if entered time can't be set
    today, then will be returned date of tomorrow, else date of today.
    """
    now = datetime.datetime.today()
    if time_wakeup[0] == now.hour and time_wakeup[1] > now.minute or time_wakeup[0] > now.hour:
        return (now.day, now.month)
    else:
        delta = datetime.timedelta(days=1)
        tomorrow = now + delta
        return (tomorrow.day, tomorrow.month)


def ask_suspend() -> bool:
    """
    This function asks the user, if standby mode is required now. Any
    word or character means standby required, empty input means don't.
    """
    try:
        return bool(input("Suspend? 1 - yes, '' - no : "))
    except EOFError:
        print("Input interrupted. EXIT.")
        sys.exit()


if __name__ == "__main__":
    main()
