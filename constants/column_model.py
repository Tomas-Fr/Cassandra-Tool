from constants.model_wrapper import ModelWrapper
from constants.common import OrderBy


class ColumnModel(ModelWrapper):
    def __init__(self, name: str = "", type: str = "", is_partition_key: bool = False, is_clustering_key: bool = False,
                 create_index: bool = False, order_by: OrderBy = OrderBy.ASC.value) -> None:
        super().__init__(
            name                = name,
            type                = type,
            is_partition_key      = is_partition_key,
            is_clustering_key   = is_clustering_key,
            create_index        = create_index,
            order_by            = order_by
        )