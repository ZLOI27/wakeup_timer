import socket
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


WEBSITE = "https://www.rbc.ru"
TIME_OF_NEWS = 20  # Seconds
TIME_WAKEUP = "05:30"


def main() -> None:
    """
    This programm set timer to wakeup system from suspend and opens
    a browser and website with news.
    """
    os.system(f"sudo rtcwake -u --date {get_time_wakeup(TIME_WAKEUP)}")
    if int(input("Suspend? 1 - yes, 0 - no :")):
        os.system("sudo systemctl suspend")
    time.sleep(5)
    while True:
        if check_internet():
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 20%")
            driver = webdriver.Firefox()
            driver.get(WEBSITE)
            driver.maximize_window()
            time.sleep(2)
            full_screen_on(driver)
            time.sleep(20)
            site_sound_on(driver)
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 50%")
            time.sleep(600)
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


def full_screen_on(driver: object) -> None:
    """Fullscreen videostream on the website."""
    full_screen_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__fullscreen"
    )
    full_screen_btn.click()
    full_screen_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__fullscreen"
    )
    full_screen_btn.click()


def site_sound_on(driver: object) -> None:
    """Turn on the sound on the website."""
    volume_btn = driver.find_element(
            By.CLASS_NAME, "video-player__controls__volume"
    )
    volume_btn.click()


def get_time_wakeup(TIME_WAKEUP) -> str:
    """
    This function asks you to enter the time in the format hh*mm or
    h*mm (* is any character) and processes it. If no time is entered,
    then the standard time is taken from the constant.
    """
    while True:
        time = input("Enter time hh:mm : ").strip()
        length = len(time)
        time_wakeup = ""
        if 4 <= length <= 5:
            if (
                (not time[-3].isdigit())
                and time[:-3].isdigit()
                and time[-2:].isdigit()
                and (00 <= int(time[-2:]) <= 59)
                and (00 <= int(time[:-3]) <= 23)
            ):
                time_wakeup = time[:-3] + ":" + time[-2:]
                break
            else:
                continue
        elif length == 0:
            time_wakeup = TIME_WAKEUP
            break
    return time_wakeup


if __name__ == "__main__":
    main()
