from typing import List
from constants.model_wrapper import ModelWrapper
from constants.column_model import ColumnModel


class CreateTableModel(ModelWrapper):
    def __init__(self, key_space: str = "", name: str = "", columns: List[ColumnModel] = []) -> None:
        super().__init__(
            key_space = key_space,
            name = name,
            columns = columns
        )