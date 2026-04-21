
from PySide6.QtCore import Qt, QAbstractTableModel

class GridModel(QAbstractTableModel):
    def __init__(self, rows, columns):
        super().__init__()
        self._all_rows = rows[:]
        self._rows = rows[:]
        self.columns = columns
        self._filters = {}
        self._sort_field = None
        self._sort_order = None

    def rowCount(self, parent=None): return len(self._rows)
    def columnCount(self, parent=None): return len(self.columns)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]['title']

    def data(self, index, role):
        row = self._rows[index.row()]
        col = self.columns[index.column()]
        val = row.get(col['field'])
        if role == Qt.DisplayRole:
            if col.get('format') and hasattr(val, 'strftime'):
                return val.strftime('%d/%m/%Y')
            return '' if val is None else str(val)
        if role == Qt.TextAlignmentRole:
            return col.get('align', Qt.AlignLeft | Qt.AlignVCenter)
        if role == Qt.EditRole:
            return val

    def flags(self, index):
        f = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if self.columns[index.column()].get('editable'):
            f |= Qt.ItemIsEditable
        return f

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._rows[index.row()][self.columns[index.column()]['field']] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def sort(self, column, order=Qt.AscendingOrder):
        field = self.columns[column]['field']
        self.layoutAboutToBeChanged.emit()
        self._rows.sort(key=lambda r: r.get(field), reverse=(order == Qt.DescendingOrder))
        self.layoutChanged.emit()
