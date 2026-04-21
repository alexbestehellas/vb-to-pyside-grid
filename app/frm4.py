# app/frm4.py

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import Qt

from core.glbData import GlbData


class Frm4(QDialog):
    """
    Dynamic grid form.
    Replacement of VB frm4.xaml / frm4.xaml.vb
    Stage 2: Load metadata (SysFrm, SysFrmGrd)
    """

    def __init__(self, cod_sys_frm: int, parent=None):
        super().__init__(parent)

        self.cod_sys_frm = cod_sys_frm

        # Metadata containers
        self.sysfrm_row = None
        self.sysfrm_grd_rows = []

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

        # Load metadata
        self._load_metadata()

    # ------------------------------------------------------------
    # Metadata loading
    # ------------------------------------------------------------

    def _load_metadata(self):
        """
        Load SysFrm and SysFrmGrd metadata
        """
        glb = GlbData()

        # Load SysFrm row
        for row in glb.get_table("SysFrm"):
            if row["Cod"] == self.cod_sys_frm:
                self.sysfrm_row = row
                break

        if not self.sysfrm_row:
            raise RuntimeError(f"SysFrm not found: Cod={self.cod_sys_frm}")

        # Update window title from metadata
        self.setWindowTitle(self.sysfrm_row.get("FrmCaption", "Frm4"))

        # Load SysFrmGrd rows (grids of this form)
        self.sysfrm_grd_rows = [
            r for r in glb.get_table("SysFrmGrd")
            if r["CodSysFrm"] == self.cod_sys_frm
        ]

        # Sort grids by row/column layout
        self.sysfrm_grd_rows.sort(
            key=lambda r: (r.get("RowNo", 0), r.get("ColNo", 0))
        )

    # ------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
