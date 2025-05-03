import os


def main() -> None:
    """
    This programm set timer to wakeup system from suspend.
    """
    time = input('Enter time hh:mm: ').strip()
    os.system(f'sudo rtcwake -u --date {time}')
    os.system('sudo systemctl suspend') # Temporary line
    os.system('xdg-open https://rbc.ru')


if __name__ == '__main__':
    main()

