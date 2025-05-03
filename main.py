import socket
import os
import time


def main() -> None:
    """
    This programm set timer to wakeup system from suspend.
    """
    time_wakeup = input("Enter time hh:mm: ").strip()
    os.system(f"sudo rtcwake -u --date {time_wakeup}")
    os.system("sudo systemctl suspend") # Temporary line
    time.sleep(5)
    while True:
        if check_internet():
            os.system("xdg-open https://www.rbc.ru")
            break
        else:
            print("Disable internet connection")
            time.sleep(3)


def check_internet(host='8.8.8.8', port=53, timeout=3):
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
