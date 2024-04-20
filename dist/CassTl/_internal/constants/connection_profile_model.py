from constants.model_wrapper import ModelWrapper


class ConnectionProfileModel(ModelWrapper):
    def __init__(self, connection_name: str = "",
                 host: str = "",
                 port: int = 0,
                 username: str = "",
                 password: bytes = None) -> None:
        super().__init__(
            connection_name = connection_name,
            host            = host,
            port            = port,
            username        = username,
            password        = password
        )