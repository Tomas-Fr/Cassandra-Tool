from typing import List, Union
from constants.common import ErrorTitles, ReplicationClass
from constants.utils import pop_up_error
from constants.connection_model import Connection
from constants.create_table_model import CreateTableModel
from constants.create_key_space_model import CreateKeySpaceModel
from constants.column_model import ColumnModel
from constants.utils import remove_empty_strings


class CassandraManager:
    def __init__(self, connection: Connection) -> None:
        self.cluster = connection.cluster
        self.session = self.cluster.connect()


    #######################################################################################################
    # Create keyspace
    def create_key_space(self: 'CassandraManager',
                         key_space_model: CreateKeySpaceModel) -> bool:
        if not self.check_create_key_space_prerequisites(key_space_model):
            return False

        query = self.generate_create_key_space_query(key_space_model)

        try:
            self.session.execute(query)
        except Exception as message:
            pop_up_error(ErrorTitles.Error.value, message)
            return False
        return True


    def generate_create_key_space_query(self: 'CassandraManager',
                                        key_space_model: CreateKeySpaceModel) -> str:
        query = f"CREATE KEYSPACE {key_space_model.name}"
        query = f"{query} WITH replication = {{'class': '{key_space_model.replication_class}'"
        query = self.add_replication_factor(key_space_model, query)
        query = self.add_datacenters_replication_factors(key_space_model, query)
        query = self.add_durable_writes(key_space_model, query)
        return query

    def add_replication_factor(self: 'CassandraManager',
                               key_space_model: CreateKeySpaceModel, query: str) -> str:
        if key_space_model.replication_factor > 0:
            query = f"{query}, 'replication_factor': {key_space_model.replication_factor}"
        return query

    def add_datacenters_replication_factors(self: 'CassandraManager',
                                            key_space_model: CreateKeySpaceModel, query: str) -> str:
        if key_space_model.replication_class == ReplicationClass.NetworkTopologyStrategy.value:
            for datacenter in key_space_model.datacenters:
                query = f"{query}, '{datacenter.name}': {datacenter.replication_factor}"
        return f"{query}}}"

    def add_durable_writes(self: 'CassandraManager',
                           key_space_model: CreateKeySpaceModel, query: str) -> str:
        if key_space_model.durable_writes is False:
            query = f"{query} AND durable_writes = false"
        return f"{query};"

    def check_create_key_space_prerequisites(self: 'CassandraManager',
                                             key_space_model: CreateKeySpaceModel) -> bool:
        try:
            self.check_empty_space_in_key_space_name(key_space_model)
            self.check_replication_factor_with_simple_strategy(key_space_model)
            self.check_replication_factor_with_network_topology_strategy(key_space_model)
        except Exception as message:
            pop_up_error(ErrorTitles.Error.value, message)
            return False
        else:
            return True

    def check_empty_space_in_key_space_name(self: 'CassandraManager',
                                            key_space_model: CreateKeySpaceModel) -> Union[None, Exception]:
        if " " in key_space_model.name:
            raise Exception(f"Keyspace name '{key_space_model.name}' is not valid. (It cannot include empty spaces.)")

    def check_replication_factor_with_simple_strategy(self: 'CassandraManager',
                                                      key_space_model: CreateKeySpaceModel) -> Union[None, Exception]:
        if self.is_replication_factor_zero(key_space_model) and self.is_simple_strategy(key_space_model):
            raise Exception(f"Replication factor can not be 0, when SimpleStrategy class is selected.")

    def check_replication_factor_with_network_topology_strategy(self: 'CassandraManager',
                                                                key_space_model: CreateKeySpaceModel) -> Union[None, Exception]:
        if self.is_network_topology_strategy(key_space_model):
            if self.no_datacentrum_has_replication_factor(key_space_model):
                raise Exception("Configuration for at least one datacenter must be present.")

    def is_simple_strategy(self: 'CassandraManager',
                           key_space_model: CreateKeySpaceModel) -> bool:
        return key_space_model.replication_class == ReplicationClass.SimpleStrategy.value

    def is_network_topology_strategy(self: 'CassandraManager',
                                     key_space_model: CreateKeySpaceModel) -> bool:
        return key_space_model.replication_class == ReplicationClass.NetworkTopologyStrategy.value

    def is_replication_factor_zero(self: 'CassandraManager',
                                   key_space_model: CreateKeySpaceModel) -> bool:
        return key_space_model.replication_factor == 0

    def no_datacentrum_has_replication_factor(self: 'CassandraManager',
                                              key_space_model: CreateKeySpaceModel) -> bool:
        return (self.is_replication_factor_zero(key_space_model) and
                not any(datacenter.replication_factor for datacenter in key_space_model.datacenters))

    #######################################################################################################
    # Delete keyspace
    def delete_key_space(self: 'CassandraManager',
                         key_space: str) -> None:
        query = f"DROP KEYSPACE {key_space};"
        try:
            self.session.execute(query)
        except Exception as message:
            pop_up_error(ErrorTitles.Error.value, message)

    #######################################################################################################
    # Create table
    def create_table(self: 'CassandraManager',
                     table_model: CreateTableModel) -> bool:
        partition_keys = [column.name for column in table_model.columns if column.is_partition_key]
        clustering_keys = [column.name for column in table_model.columns if self.check_clustering_key(column)]

        if not self.check_create_table_prerequisites(table_model, partition_keys, clustering_keys):
            return False

        query = self.generate_ddl(table_model, partition_keys, clustering_keys)

        queries = remove_empty_strings(query.split(';'))
        is_success = True
        for query in queries:
            try:
                self.session.execute(query)
            except Exception as message:
                pop_up_error(ErrorTitles.Error.value, message)
                is_success = False
        return is_success

    def add_columns_with_types(self: 'CassandraManager',
                               table_model: CreateTableModel, query: str) -> Union[str, Exception]:
        for column in table_model.columns:
            query = f'{query}\n    {column.name} {column.type},'
        return query

    def add_partition_keys(self: 'CassandraManager',
                           partition_keys: List[str], query: str) -> str:
        partition_keys_query = f"{', '.join(partition_keys)}"
        if len(partition_keys) > 1:
            partition_keys_query = f"({partition_keys_query})"
        query = f"{query}\n    PRIMARY KEY ({partition_keys_query}"
        return query

    def add_clustering_keys(self: 'CassandraManager',
                            clustering_keys: List[str], query: str) -> str:
        if clustering_keys:
            clustering_keys_query = f"{', '.join(clustering_keys)}"
            query = f"{query}, {clustering_keys_query}"
        return f"{query})\n)"

    def add_clustering_order(self: 'CassandraManager',
                             table_model: CreateTableModel, query: str) -> str:
        clustering_keys_order_by = [f"{column.name} {column.order_by}" for column in table_model.columns if self.check_clustering_key(column)]
        if clustering_keys_order_by:
            query = f"{query} WITH CLUSTERING ORDER BY ({', '.join(clustering_keys_order_by)})"
        return f"{query};"

    def add_indexes(self: 'CassandraManager', table_model: CreateTableModel, query: str) -> str:
        indexes = [column.name for column in table_model.columns if column.create_index]

        if not indexes:
            return query

        for index in indexes:
            query = f"{query}\nCREATE INDEX IF NOT EXISTS ON {table_model.key_space}.{table_model.name} ({index});"

        return query

    def check_at_least_two_columns_in_table(self: 'CassandraManager',
                                            table_model: CreateTableModel) -> Union[None, Exception]:
        if len(table_model.columns) < 2:
            raise Exception(f"Table '{table_model.name}' must have at least two columns.")

    def check_at_least_one_partition_key(self: 'CassandraManager',
                                         table_model: CreateTableModel, partition_keys: List[str]) -> Union[None, Exception]:
        if len(partition_keys) < 1:
            raise Exception(f"Table '{table_model.name}' must have at least one partition key.")

    def check_partition_clustering_keys_not_match(self: 'CassandraManager',
                                                  partition_keys: List[str], clustering_keys: List[str]) -> Union[None, Exception]:
        common_elements = set(clustering_keys) & set(partition_keys)
        if common_elements:
            raise Exception(f"Columns '{common_elements}' cannot serve as both the partition key and the clustering key simultaneously.")

    def check_empty_space_in_table_name(self: 'CassandraManager',
                                        table_model: CreateTableModel) -> Union[None, Exception]:
        if " " in table_model.name:
            raise Exception(f"Table name '{table_model.name}' is not valid. (It cannot include empty spaces.)")

    def check_empty_space_in_columns_names(self: 'CassandraManager',
                                           table_model: CreateTableModel) -> Union[None, Exception]:
        for column in table_model.columns:
            if " " in column.name:
                raise Exception(f"Column name '{column.name}' is not valid. (It cannot include empty spaces.)")

    def check_create_table_prerequisites(self: 'CassandraManager',
                                         table_model: CreateTableModel,
                                         partition_keys: List[str],
                                         clustering_keys: List[str]) -> bool:
        try:
            self.check_empty_space_in_table_name(table_model)
            self.check_empty_space_in_columns_names(table_model)
            self.check_at_least_two_columns_in_table(table_model)
            self.check_at_least_one_partition_key(table_model, partition_keys)
            self.check_partition_clustering_keys_not_match(partition_keys, clustering_keys)
        except Exception as message:
            pop_up_error(ErrorTitles.Error.value, message)
            return False
        else:
            return True

    def check_clustering_key(self: 'CassandraManager', column: ColumnModel) -> bool:
        return column.is_clustering_key

    def generate_ddl(self, table_model: CreateTableModel, partition_keys: List[str], clustering_keys: List[str]) -> str:
        query = f"CREATE TABLE {table_model.key_space}.{table_model.name} ("
        query = self.add_columns_with_types(table_model, query)
        query = self.add_partition_keys(partition_keys, query)
        query = self.add_clustering_keys(clustering_keys, query)
        query = self.add_clustering_order(table_model, query)
        query = self.add_indexes(table_model, query)
        return query

    #######################################################################################################
    # Delete table
    def delete_table(self: 'CassandraManager', key_space: str, table: str) -> None:
        query = f"DROP TABLE IF EXISTS {key_space}.{table};"
        self.session.execute(query)