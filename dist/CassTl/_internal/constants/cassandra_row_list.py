from constants.model_wrapper import ModelWrapper


class CassandraRowList:
    def __init__(self: 'CassandraRowList', cassandra_table_model) -> None:
        self.table = cassandra_table_model
        self.new_rows = []


    def add_row(self: 'CassandraRowList') -> None:
        new_row = ModelWrapper(**{column: None for column in self.table.header_data})
        self.new_rows.append(new_row)
        self.table.data.append(new_row)
        self.table.layoutChanged.emit()

    def remove_rows(self: 'CassandraRowList') -> None:
        self.new_rows = []