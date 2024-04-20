from PyQt6.QtGui import QStandardItemModel, QStandardItem
from constants.common import NO_TABLE, ErrorTitles
from constants.utils import pop_up_error
from constants.connection_model import Connection
from cassandra.cluster import Session


class CustomCassandraTreeModel:
    def __init__(self: 'CustomCassandraTreeModel', connections: list[Connection]) -> None:
        self.connections = connections
        self.cassandra_data = self.get_cassandra_structure()


    def __try_connect(self: 'CustomCassandraTreeModel', connection: Connection) -> Session:
        session = None
        try:
            session = connection.cluster.connect()
        except Exception as message:
            pop_up_error(ErrorTitles.Connection_profiles.value, message)
        finally:
            return session

    def get_cassandra_structure(self: 'CustomCassandraTreeModel') -> dict:
        structure = {}

        for connection in self.connections:
            session = self.__try_connect(connection)
            keyspace_metadata_list = connection.cluster.metadata.keyspaces.values()
            connection_structure = {}

            for keyspace_metadata in keyspace_metadata_list:
                keyspace_name = keyspace_metadata.name
                keyspace_structure = {}

                for table_metadata in keyspace_metadata.tables.values():
                    table_name = table_metadata.name
                    keyspace_structure[table_name] = {}

                connection_structure[keyspace_name] = keyspace_structure

            structure[connection.connection_profile_name] = connection_structure
            if session is not None:
                session.shutdown()
        return structure

    def create_custom_model(self: 'CustomCassandraTreeModel') -> QStandardItemModel:
        custom_model = QStandardItemModel()

        for category, subcategories in self.cassandra_data.items():
            parentItem = QStandardItem(category)

            for subcategory, subcategory_values in subcategories.items():
                subcategory_item = QStandardItem(subcategory)

                if not subcategory_values:
                    child_item = QStandardItem(NO_TABLE)
                    subcategory_item.appendRow(child_item)

                for key, value in subcategory_values.items():
                    child_item = QStandardItem(key)
                    subcategory_item.appendRow(child_item)

                parentItem.appendRow(subcategory_item)

            custom_model.appendRow(parentItem)

        return custom_model