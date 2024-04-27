from constants.model_wrapper import ModelWrapper


class DatacenterModel(ModelWrapper):
    def __init__(self, name: str = "", replication_factor: int = 0) -> None:
        super().__init__(
            name                = name,
            replication_factor  = replication_factor
        )