# app/frm4.py

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import Qt


class Frm4(QDialog):
    """
    Dynamic grid form.
    Replacement of VB frm4.xaml / frm4.xaml.vb
    Stage 1: Skeleton & layout only (no grids yet).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window setup
        self.setWindowTitle("Frm4")
        self.setModal(True)
        self.resize(1000, 600)

        # Root layout (vertical)
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(10, 10, 10, 10)
        self._root_layout.setSpacing(10)

        # Central container widget
        self._central_widget = QWidget(self)
        self._root_layout.addWidget(self._central_widget)

        # Grid layout where grids will be placed
        self._grid_layout = QGridLayout(self._central_widget)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(10)

    # ------------------------------------------------------------
    # Lifecycle hooks (will be extended later)
    # ------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
