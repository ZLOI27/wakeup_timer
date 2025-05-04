import socket, os, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def main() -> None:
    """
    This programm set timer to wakeup system from suspend.
    """
    time_wakeup = input("Enter time hh:mm: ").strip() # It is required to add check correct input
    os.system(f"sudo rtcwake -u --date {time_wakeup}") # It is required to add 'try except'
    os.system("sudo systemctl suspend") # Temporary line -----
    time.sleep(5)
    while True:
        if check_internet():
            driver = webdriver.Firefox()
            driver.get("https://www.rbc.ru")
            break
        else:
            print("Disable internet connection")
            time.sleep(2)


def check_internet(host='8.8.8.8', port=53, timeout=3) -> bool:
    """
    Testing internet conection with DNS-server Google (8.8.8.8)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


if __name__ == '__main__':
    main()
