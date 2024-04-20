from PyQt6.QtCore import QSortFilterProxyModel, QModelIndex


class CustomFilterProxyModel(QSortFilterProxyModel):
    def __init__(self: 'CustomFilterProxyModel') -> None:
        super().__init__()

    def filterAcceptsRow(self: 'CustomFilterProxyModel', source_row: int, source_parent: QModelIndex) -> bool:
        filter_text = self.filterRegularExpression().pattern()
        if not filter_text:
            return True
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        name = source_model.data(index.siblingAtColumn(0))
        host = source_model.data(index.siblingAtColumn(1))
        return filter_text in str(name) or filter_text in str(host)
