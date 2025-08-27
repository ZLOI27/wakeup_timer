#!/usr/bin/env python3

import socket
import os
import time
import sys
import yaml
import datetime
import asyncio


STREAM = "http://online.video.rbc.ru/online/rbctv_1080p/index.m3u8"
VIDEOPLAYER = "mpv"
OPTION = "--fullscreen=yes"
TIME_OF_NEWS = 3600  # Seconds
TIME_WAKEUP = (5, 30)


async def main() -> None:
    """
    This programm set timer to wakeup system from suspend and open videostream.
    """
    default_configs_obj = DefaultConfigs()
    suspend = None
    config = get_config_from_file(default_configs_obj)
    if config == None:
        create_configfile(default_configs_obj)
        config = get_config_from_file(default_configs_obj)
        if config == None:
            print("\033[31The program could not create a configuration file. Exit.\033[0m")
            sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 's':
        time_wakeup = (config[0], config[1])
        suspend = bool(config[2])
    else:
        time_wakeup = ask_time_wakeup(TIME_WAKEUP)
        date_wakeup = ask_date_wakeup(time_wakeup)

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

    for i in range(30):
        if check_internet():
            print("\033[32mInternet conection is OK!\033[0m")
            os.system(f"{VIDEOPLAYER} {OPTION} {STREAM} &")
            await asyncio.gather(control_volume(), asyncio.sleep(TIME_OF_NEWS))
            os.system("systemctl suspend")
            break
        else:
            print("\033[31mDisable internet connection, try again...\033[0m")
            time.sleep(2)
    print('PC not connected to internet.')
    write_log('PC not connected to internet.')
    os.system("systemctl suspend") # FIXME: need add Exeption


def check_internet(host="8.8.8.8", port=53, timeout=3) -> bool:
    """Testing internet conection with DNS-server Google (8.8.8.8)."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def ask_time_wakeup(TIME_WAKEUP: tuple) -> tuple:
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


def ask_date_wakeup(time_wakeup: tuple) -> tuple:
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


def get_config_from_file(default_configs_obj: 'DefaultConfigs') -> any:
    """This function open config file and read time."""
    try:
        with open(file=f'{default_configs_obj.PATH_TO_USER_CONFIGFILE}', mode='r', encoding='utf-8',) as config_file:
            data_dict = yaml.safe_load(config_file)
            return (data_dict['date_time']['hour'], data_dict['date_time']['minute'], data_dict['common']['suspend'])
    except OSError as error:
        print("\033[31mProblems with the config file, see log.txt.\033[0m")
        write_log(str(error))
        return None
        


def write_log(message: str, path=os.path.expanduser('~/Desktop/log.txt')) -> bool:
    """This function write errors in log.txt"""
    try:
        with open(path, mode='a', encoding='utf-8') as file_log:
            file_log.write(f"\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}")
        return True
    except OSError as error:
        print("\033[31mProblems with the log file.\033[0m")
        print(error)
        return False


async def control_volume(init_vol=20, percents_vol=15, max_vol=100, delay=300, cycles=4) -> bool:
    """
    This function sleeps for the required number of seconds, increases 
    the volume, and repeats the process as many times as necessary.
    """
    os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {init_vol}%")
    for i in range(cycles):
        os.system(f"pactl get-sink-volume @DEFAULT_SINK@")
        await asyncio.sleep(delay)
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ +{percents_vol}%")
    return True


def create_configfile(default_configs_obj: 'DefaultConfigs'):
    """Сreating a file with user configurations in case it is missing."""
    try:
        with open(file=f'{default_configs_obj.PATH_TO_USER_CONFIGFILE}', mode='w', encoding='utf-8') as config_file:
            yaml.safe_dump(default_configs_obj.create_data_for_yamlfile(), config_file)
    except OSError as error:
        print("\033[31mProblems with creating a config file.\033[0m")
        write_log(str(error))


class DefaultConfigs:
    """
    This singletone is used for store configs.
    This is done for educational purposes.
    """
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    

    def __init__(self):
        self.TIME_WAKEUP = (5, 30)
        self.SUSPEND = False
        self.TIME_OF_NEWS = 3600  # Seconds
        self.VIDEOPLAYER = "mpv"
        self.OPTION = "--fullscreen=yes"
        self.STREAM = "http://online.video.rbc.ru/online/rbctv_1080p/index.m3u8"
        self.INIT_VOLUME = 20
        self.PERCENTS_VOLUME = 15
        self.MAX_VOLUME = 100
        self.DELAY_RISE_VOLUME = 300
        self.CYCLES_RISE_VOLUME = 4
        self.PATH_TO_LOGFILE = os.path.join(os.getcwd(), 'log.txt')
        self.PATH_TO_USER_CONFIGFILE = os.path.join(os.getcwd(), 'user_config.yaml')


    def create_data_for_yamlfile(self) -> dict:
        data = {
            'date_time': {
                'hour': self.TIME_WAKEUP[0],
                'minute': self.TIME_WAKEUP[1],
                'time_of_news': self.TIME_OF_NEWS,
                },
            'common': {
                'suspend': False,
            },
            'stream': {
                'videoplayer': self.VIDEOPLAYER,
                'option': self.OPTION,
                'stream': self.STREAM,
                },
            'volume_config': {
                'init_volume': self.INIT_VOLUME,
                'percent_volume': self.PERCENTS_VOLUME,
                'max_volume': self.MAX_VOLUME,
                'delay_rise_volume': self.DELAY_RISE_VOLUME,
                'cycles_rise_volume': self.CYCLES_RISE_VOLUME,
                },
            'path': {
                'path_to_logfile': self.PATH_TO_LOGFILE,
                'path_to_user_configfile': self.PATH_TO_USER_CONFIGFILE,
                },
            }
        return data


if __name__ == "__main__":
    asyncio.run(main())
