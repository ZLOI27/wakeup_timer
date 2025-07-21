class default_configs:
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
        self.TON_BEFORE_RISE_VOL = 150  # Time of news before rise volume(seconds)
        self.TIME_OF_NEWS = 3600  # Seconds
        self.OPTION = "--fullscreen=yes"
        self.VIDEOPLAYER = "mpv"
        self.STREAM = "http://online.video.rbc.ru/online/rbctv_1080p/index.m3u8"
