from typing import List
from constants.model_wrapper import ModelWrapper
from constants.datacenter_model import DatacenterModel


class CreateKeySpaceModel(ModelWrapper):
    def __init__(self,
                 name: str = "",
                 replication_class: str = "",
                 replication_factor: int = 0,
                 durable_writes: bool = True,
                 datacenters: List[DatacenterModel] = []) -> None:
        super().__init__(
            name = name,
            replication_class = replication_class,
            replication_factor = replication_factor,
            durable_writes = durable_writes,
            datacenters = datacenters
        )