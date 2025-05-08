import socket
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


WEBSITE = "https://www.rbc.ru"
TIME_OF_NEWS = 20


def main() -> None:
    """
    This programm set timer to wakeup system from suspend and opens
    a browser and website with news.
    """
    time_wakeup = input(
        "Enter time hh:mm: "
    ).strip()  # It is required to add check correct input
    os.system(
        f"sudo rtcwake -u --date {time_wakeup}"
    )  # It is required to add 'try except'
    os.system("sudo systemctl suspend")  # Temporary line -----
    time.sleep(5)
    while True:
        if check_internet():
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 20%")
            driver = webdriver.Firefox()
            driver.get(WEBSITE)
            driver.maximize_window()
            time.sleep(2)
            full_screen_on(driver)
            time.sleep(25)
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
    full_screen_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__fullscreen"
    )
    full_screen_btn.click()
    full_screen_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__fullscreen"
    )
    full_screen_btn.click()


def site_sound_on(driver: object) -> None:
    volume_btn = driver.find_element(
        By.CLASS_NAME, "video-player__controls__volume"
    )
    volume_btn.click()


if __name__ == "__main__":
    main()
