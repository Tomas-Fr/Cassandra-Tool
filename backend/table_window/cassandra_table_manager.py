import re
from typing import Any, List, Optional, Tuple, Union
from PyQt6.QtWidgets import QPlainTextEdit
from constants.utils import pop_up_error
from constants.common import ErrorTitles
from constants.show_result_utils import ShowResultUtils
from constants.insert_row_utils import InsertRowUtils
from cassandra.cluster import Cluster, Session, ResultSet, PreparedStatement


class CassandraTableManager:
    def __init__(self: 'CassandraTableManager',
                 cluster: Cluster,
                 session: Session,
                 key_space: str,
                 table: str,
                 results_plain_text_edit: QPlainTextEdit,
                 result_statistics_plain_text_edit: QPlainTextEdit) -> None:
        self.cluster = cluster
        self.session = session
        self.key_space = key_space
        self.table = table
        self.results_plain_text_edit = results_plain_text_edit
        self.result_statistics_plain_text_edit = result_statistics_plain_text_edit
        self.header_data = self.get_column_names()
        self.column_types = self.get_column_types()
        self.ddl = self.get_ddl()
        self.show_result_utils = ShowResultUtils(self.results_plain_text_edit, self.result_statistics_plain_text_edit)
        self.insert_row_utils = InsertRowUtils()


    def get_ddl(self: 'CassandraTableManager') -> Union[ResultSet, Exception]:
        try:
            query = f"DESCRIBE TABLE {self.key_space}.{self.table};"
            return self.session.execute(query).all()
        except Exception as error_message:
            pop_up_error(ErrorTitles.Db_Cassandra_error.value, error_message)

    def select_all(self: 'CassandraTableManager') -> Union[ResultSet, Exception]:
        try:
            query = f"SELECT * FROM {self.key_space}.{self.table};"
            return self.session.execute(query).all()
        except Exception as error_message:
            pop_up_error(ErrorTitles.Db_Cassandra_error.value, error_message)

    def delete_row(self: 'CassandraTableManager', data: List[dict], row_index: int) -> None:
        primary_keys, query = self.prepare_delete_query()

        primary_key_values = self.get_primary_keys_values(data, row_index, primary_keys)

        try:
            self.session.execute(query, primary_key_values)
        except Exception as error_message:
            error_message = f"{ErrorTitles.Failed.value} {error_message}"
            self.show_result_utils.show_result(error_message)

    def get_column_types(self: 'CassandraTableManager') -> Union[ResultSet, Exception]:
        try:
            query = f"""SELECT column_name, type
                            FROM system_schema.columns
                                WHERE keyspace_name = '{self.key_space}' AND
                                    table_name = '{self.table}'"""
            return self.session.execute(query).all()
        except Exception as error_message:
            pop_up_error(ErrorTitles.Db_Cassandra_error.value, error_message)

    def get_column_names(self: 'CassandraTableManager') -> Union[List[str], Exception]:
        try:
            query = f"""SELECT * FROM {self.key_space}.{self.table}"""
            return self.session.execute(query).column_names
        except Exception as error_message:
            pop_up_error(ErrorTitles.Db_Cassandra_error.value, error_message)

    def prepare_insert_query(self: 'CassandraTableManager') -> PreparedStatement:
        return self.session.prepare(
            f"""INSERT INTO {self.key_space}.{self.table}
                ({", ".join(self.header_data)})
                VALUES ({", ".join(['?' for _ in range(len(self.header_data))])});""")

    def insert_row(self: 'CassandraTableManager', query: PreparedStatement, row: List[Any]) -> Optional[Exception]:
        try:
            self.session.execute(query, row)
        except Exception as error_message:
            return f"""{ErrorTitles.Failed.value} {error_message}\nquery: {self.select_query(query)}\ndata: {row}\n"""

    def select_query(self: 'CassandraTableManager', prepared_query: PreparedStatement) -> Union[str, PreparedStatement]:
        pattern = r'<PreparedStatement query="([^"]+)"'
        match = re.search(pattern, str(prepared_query))
        if match:
            return match.group(1)
        else:
            return prepared_query

    def prepare_update_query(self: 'CassandraTableManager') -> Tuple[List[str], PreparedStatement]:
        primary_keys = self.get_primary_keys()
        primary_key_condition = self.get_primary_key_condition(primary_keys)

        query = self.session.prepare(
            f"""UPDATE {self.key_space}.{self.table}
                SET
                {self.generate_set_clauses_for_update(primary_keys)}
                WHERE
                {primary_key_condition}""")

        return (primary_keys, query)

    def update_row(self: 'CassandraTableManager', data: List[dict], row_index: int, row: dict) -> Optional[Exception]:
        primary_keys, query = primary_keys, query = self.prepare_update_query()

        values = self.prepare_values_for_update_query(data, row_index, row, primary_keys)

        try:
            self.session.execute(query, values)
        except Exception as error_message:
            error_message = f"{ErrorTitles.Failed.value} {error_message}"
            self.show_result_utils.show_result(error_message)
        else:
            self.show_result_utils.show_success()

    def prepare_values_for_update_query(self: 'CassandraTableManager',
                                        data: List[dict],
                                        row_index: int,
                                        row: dict,
                                        primary_keys: List[str]) -> List[Any]:
        primary_key_values = self.get_primary_keys_values(data, row_index, primary_keys)
        prepared_row = self.insert_row_utils.prepare_row(self.column_types, row)
        primary_key_values_prepared = self.prepare_primary_keys(prepared_row, primary_key_values)

        return prepared_row[len(primary_key_values):] + primary_key_values_prepared

    def prepare_primary_keys(self: 'CassandraTableManager', prepared_row: List[Any], primary_key_values: List[Any]) -> List[Any]:
        primary_key_values_prepared = []
        for item_row in prepared_row:
            for prim_key in primary_key_values:
                if str(item_row) == str(prim_key):
                    primary_key_values_prepared.append(item_row)
        return primary_key_values_prepared

    def generate_set_clauses_for_update(self: 'CassandraTableManager', primary_keys: List[str]) -> str:
        column_names = self.get_column_names()
        return ", \n".join(f"{column} = ?" for column in column_names[len(primary_keys):])

    def get_primary_keys_values(self: 'CassandraTableManager', data: List[dict], row_index: int, primary_keys: List[str]) -> List[str]:
        primary_key_values = []
        for primary_key in primary_keys:
            primary_key_values.append(getattr(data[row_index], primary_key))
        return primary_key_values

    def get_primary_key_condition(self: 'CassandraTableManager', primary_keys: List[str]) -> Union[str, Exception]:
        if not primary_keys:
            raise Exception("No primary keys found.")
        conditions = " AND ".join(f"{column} = ?" for column in primary_keys)
        return conditions

    def get_primary_keys(self: 'CassandraTableManager') -> Union[List[str], None]:
        try:
            query = f"""SELECT column_name, kind
                            FROM system_schema.columns
                                WHERE keyspace_name = '{self.key_space}' AND
                                    table_name = '{self.table}'"""
            rows = self.session.execute(query).all()
            return [row.column_name for row in rows if row.kind == "partition_key" or row.kind == "clustering"]
        except Exception as error_message:
            pop_up_error(ErrorTitles.Db_Cassandra_error.value, error_message)

    def prepare_delete_query(self: 'CassandraTableManager') -> Tuple[List[str], PreparedStatement]:
        primary_keys = self.get_primary_keys()
        primary_key_condition = self.get_primary_key_condition(primary_keys)

        query = self.session.prepare(
            f"""DELETE FROM {self.key_space}.{self.table}
                    WHERE {primary_key_condition};"""
        )
        return (primary_keys, query)
