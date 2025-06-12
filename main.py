#!/usr/bin/env python3

import socket
import os
import time
import sys
import json
import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.common.by import By


WEBSITE = "https://www.rbc.ru"
TIME_OF_NEWS = 3000  # Seconds
TON_BEFORE_RISE_VOL = 300  # Time of news before rise volume(seconds)
TIME_WAKEUP = (5, 30)


def main() -> None:
    """
    This programm set timer to wakeup system from suspend and opens
    a browser and website with news.
    """
    suspend = None
    config = get_config_from_file()
    if len(sys.argv) > 1 and sys.argv[1] == 's':
        time_wakeup = (config[0], config[1])
        suspend = bool(config[2])
    else:
        time_wakeup = get_time_wakeup(TIME_WAKEUP)
        date_wakeup = get_date_wakeup(time_wakeup)
    date_wakeup = today_or_tomorrow(time_wakeup)
    date_str = f'{date_wakeup[0]}-{date_wakeup[1]}-{date_wakeup[2]}'
    time_str = f'{time_wakeup[0]}:{time_wakeup[1]}'
    date_time_wakeup = f'{date_str} {time_str}'
    os.system(f"sudo rtcwake -u --date '{date_time_wakeup}'")
    os.system(f"sudo rtcwake -l -m show")
    if suspend == None and ask_suspend() or suspend:
        time.sleep(3)
        os.system("sudo systemctl suspend")
    while True:
        now = datetime.datetime.today()
        if (now.hour, now.minute) == time_wakeup:
            break
        else:
            time.sleep(5)
    time.sleep(5)
    while True:
        if check_internet():
            print("\033[32mInternet conection is OK!\033[0m")
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 20%")
            options = Options()
            options.page_load_strategy = 'none'
            driver = webdriver.Firefox(options=options)
            driver.get(WEBSITE)
            driver.maximize_window()
            time.sleep(4)
            fullscreen_on(driver)
            time.sleep(12)
            site_sound_on(driver)
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 50%")
            time.sleep(TON_BEFORE_RISE_VOL)
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 75%")
            time.sleep(TON_BEFORE_RISE_VOL)
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 100%")
            time.sleep(TIME_OF_NEWS)
            driver.quit()
            os.system("systemctl suspend")
            break
        else:
            print("\033[31mDisable internet connection\033[0m")
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
    for i in range(10):
        try:
            fullscreen_btn = driver.find_element(
                By.CLASS_NAME, "video-player__controls__fullscreen"
            )
            fullscreen_btn.click()
            fullscreen_btn = driver.find_element(
                By.CLASS_NAME, "video-player__controls__fullscreen"
            )
            fullscreen_btn.click()
            print("\033[32mFullscreen on. OK!\033[0m")
            break
        except Exception:
            print("\033[33mTry to turned on fullscreen mode...\033[0m")
            time.sleep(5)


def site_sound_on(driver: object) -> None:
    """Turn on the sound on the website."""
    for i in range(10):
        try:
            volume_btn = driver.find_element(
                    By.CLASS_NAME, "video-player__controls__volume"
            )
            volume_btn.click()
            print("\033[32mThe sound on the website is turned on. OK!\033[0m")
            break
        except Exception:
            print("\033[33mIt is imposible turned on sound...\033[0m")
            time.sleep(5)


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
                print("\033[31mIncorrect input, please try again...\033[0m")
                continue
    except EOFError:
        print("\033[31mInput interrupted. EXIT.\033[0m")
        sys.exit()


def get_date_wakeup(time_wakeup: tuple) -> tuple:
    """
    This function asks you to enter the date in the format dd*mm or
    d*m (* is any character, not digit) and processes it. If no date
    is entered, then the timer is set for today or tomorrow.
    """
    today = datetime.datetime.today()
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
                print("\033[31mIncorrect input, please try again...\033[0m")
                continue
            if is_valid_date(today.year, int(month), int(day)):
                return (today.year, int(month), int(day))
            else:
                print("\033[31mIncorrect input, please try again...\033[0m")
                continue
    except EOFError:
        print("\033[31mInput interrupted. EXIT.\033[0m")
        sys.exit()


def is_valid_date(year, month, day) -> bool:
    """"Just checking for existence of a date."""
    try:
        datetime.datetime(year, month, day)
        return True
    except ValueError:
        return False


def today_or_tomorrow(time_wakeup: tuple) -> tuple:
    """
    This function checks the entered time, if entered time can't be set
    today, then will be returned date of tomorrow, else date of today.
    """
    now = datetime.datetime.today()
    tw = time_wakeup
    if tw[0] == now.hour and tw[1] > now.minute or tw[0] > now.hour:
        return (now.year, now.month, now.day)
    else:
        delta = datetime.timedelta(days=1)
        tomorrow = now + delta
        return (tomorrow.year, tomorrow.month, tomorrow.day)


def ask_suspend() -> bool:
    """
    This function asks the user, if standby mode is required now. Any
    word or character means standby required, empty input means don't.
    """
    try:
        return bool(input("Suspend? 1 - yes, '' - no : "))
    except EOFError:
        print("\033[31mInput interrupted. EXIT.\033[0m")
        sys.exit()


def get_config_from_file() -> tuple:
    """This function open config file and read time, date."""
    path = '/home/zk/Desktop/config_wakeup_timer.json'
    try:
        with open(path, mode='r', encoding='utf-8',) as file:
            data_dict = json.load(file)
            return (data_dict['hour'], data_dict['minute'], data_dict['suspend'])
    except OSError:
        print("\033[31mProblems with the config file.\033[0m")
        sys.exit()


if __name__ == "__main__":
    main()
