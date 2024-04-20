import ast
from typing import Any, List, Union
from constants.common import CASSANDRA_TYPE_MAPPING
from sortedcontainers import SortedSet


class InsertRowUtils:

    def prepare_row(self: 'InsertRowUtils', column_types: str, row: dict) -> List[Any]:
        prepared_row = []
        for column, value in row.items():
            for column_type in column_types:
                if column == column_type.column_name:
                    _type = column_type.type.split('<')[0]
                    prepared_row.append(self.convert_column(value, CASSANDRA_TYPE_MAPPING[_type]))
        return prepared_row

    def convert_column(self: 'InsertRowUtils', value: str, column_type: str) -> Any:
        if not value:
            return value
        if not isinstance(value, str):
            return value
        try:
            if column_type is bool:
                return self.convert_to_bool(value)
            if column_type in [list, set, dict]:
                if value.startswith('SortedSet('):
                    sorted_set = eval(value)
                    return set(sorted_set)
                return ast.literal_eval(value)
            return column_type(value)
        except ValueError:
            return value

    def convert_to_bool(self: 'InsertRowUtils', value: str) -> Union[bool, str]:
        value_lower = value.lower()

        if value_lower == 'false':
            return False
        elif value_lower == 'true':
            return True
        elif value.isdigit() and int(value) < 2:
            return int(value) == 1
        else:
            return value