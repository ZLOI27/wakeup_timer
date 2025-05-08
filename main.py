import socket, os, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def main() -> None:
    """
    This programm set timer to wakeup system from suspend and open browser.
    """
    time_wakeup = input("Enter time hh:mm: ").strip() # It is required to add check correct input
    os.system(f"sudo rtcwake -u --date {time_wakeup}") # It is required to add 'try except'
    os.system("sudo systemctl suspend") # Temporary line -----
    time.sleep(5)
    while True:
        if check_internet():
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 20%")
            driver = webdriver.Firefox()
            driver.get('https://www.rbc.ru')
            driver.maximize_window()
            time.sleep(2)
            full_screen_btn = driver.find_element(By.CLASS_NAME, 'video-player__controls__fullscreen')
            full_screen_btn.click()
            full_screen_btn = driver.find_element(By.CLASS_NAME, 'video-player__controls__fullscreen')
            full_screen_btn.click()
            time.sleep(25)
            volume_btn = driver.find_element(By.CLASS_NAME, 'video-player__controls__volume')
            volume_btn.click()
            os.system("pactl set-sink-volume @DEFAULT_SINK@ 50%")
            time.sleep(20) #3600
            driver.quit()
            os.system("systemctl suspend")
            break
        else:
            print("Disable internet connection")
            time.sleep(2)


def check_internet(host='8.8.8.8', port=53, timeout=3) -> bool:
    """Testing internet conection with DNS-server Google (8.8.8.8)."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


if __name__ == '__main__':
    main()
