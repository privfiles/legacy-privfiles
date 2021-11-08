class B2Settings:
    def __init__(self, key_id: str, application_key: str,
                 bucket_id: str, *args, **kwargs) -> None:
        """B2 Settings.
    
        Parameters
        ----------
        key_id: str
            B2 key ID.
        application_key: str
            B2 app key.
        bucket_id: str
            Bucket to upload to.
        """

        super().__init__(*args, **kwargs)

        self.key_id = key_id
        self.application_key = application_key
        self.bucket_id = bucket_id


class CaptchaSettings:
    def __init__(self, size: int = 1, difficult_level: int = 3,
                 multicolor: bool = True, margin: bool = False) -> None:
        """Captcha settings.

        Parameters
        ----------
        size : int, optional
            by default 1
        difficult_level : int, optional
            by default 3
        multicolor : bool, optional
            by default True
        margin : bool, optional
            by default False
        """

        self.size = size
        self.difficult_level = difficult_level
        self.multicolor = multicolor
        self.margin = margin


class MongoSettings:
    def __init__(self, host: str = "localhost",
                 port: int = 27017, database: str = "privfiles"
                 ) -> None:
        """MongoDB settings.

        Parameters
        ----------
        host : str, optional
            by default "localhost"
        port : int, optional
            by default 27017
        """

        self.connection = f"mongodb://{host}:{port}"
        self.database = database


class SizeSettings:
    def __init__(self, read_size: int = 5000024, max_size: int = 943700000,
                 premium_size: int = 4295000000) -> None:
        """Size settings.

        Parameters
        ----------
        read_size : int, optional
            by default 5000024
        max_size : int, optional
            by default 943700000
        premium_size : int, optional
            by default 4295000000
        """

        self.read_size = read_size
        self.max_size = max_size
        self.premium_size = premium_size
