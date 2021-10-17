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
