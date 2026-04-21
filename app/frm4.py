# app/frm4.py

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import Qt

from core.glbData import GlbData
from app.grid.grd import GrdPY
from app.grid.model import GridModel


class Frm4(QDialog):
    """
    Dynamic grid form.
    Replacement of VB frm4.xaml / frm4.xaml.vb

    Stages included:
    - Skeleton & layout
    - Metadata loading (SysFrm, SysFrmGrd)
    - Grid creation (GrdPY + GridModel)
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

        # Root layout
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(10, 10, 10, 10)
        self._root_layout.setSpacing(10)

        # Central widget
        self._central_widget = QWidget(self)
        self._root_layout.addWidget(self._central_widget)

        # Grid layout for dynamic grids
        self._grid_layout = QGridLayout(self._central_widget)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(10)

        # Load metadata and build grids
        self._load_metadata()
        self._build_grids()

    # ------------------------------------------------------------
    # Metadata loading
    # ------------------------------------------------------------

    def _load_metadata(self):
        glb = GlbData()

        # SysFrm
        for row in glb.get_table("SysFrm"):
            if row.get("Cod") == self.cod_sys_frm:
                self.sysfrm_row = row
                break

        if not self.sysfrm_row:
            raise RuntimeError(f"SysFrm not found: Cod={self.cod_sys_frm}")

        self.setWindowTitle(self.sysfrm_row.get("FrmCaption", "Frm4"))

        # SysFrmGrd
        self.sysfrm_grd_rows = [
            r for r in glb.get_table("SysFrmGrd")
            if r.get("CodSysFrm") == self.cod_sys_frm
        ]

        self.sysfrm_grd_rows.sort(
            key=lambda r: (r.get("RowNo", 0), r.get("ColNo", 0))
        )

    # ------------------------------------------------------------
    # Grid creation
    # ------------------------------------------------------------

    def _build_grids(self):
        glb = GlbData()

        for grd_row in self.sysfrm_grd_rows:
            table_name = grd_row.get("TxtTableName")
            if not table_name:
                continue

            rows = glb.get_table(table_name)

            cols = [
                {
                    "field": c.get("ColFieldName"),
                    "title": c.get("ColCaption"),
                    "format": c.get("ColFormat"),
                    "align": Qt.AlignRight | Qt.AlignVCenter
                              if c.get("CodSysGrdTextAlignment") == 2
                              else Qt.AlignLeft | Qt.AlignVCenter,
                    "editable": bool(c.get("SwAllowEdit", False)),
                }
                for c in glb.get_table("SysFrmGrdCol")
                if c.get("CodSysFrmGrd") == grd_row.get("Cod")
                   and c.get("SwVisible", True)
            ]

            model = GridModel(rows, cols)

            grid = GrdPY()
            grid.open_with_cod_sys_frm_grd = grd_row.get("Cod")
            grid.open_with_table_name = table_name
            grid.setModel(model)

            row_no = grd_row.get("RowNo", 0)
            col_no = grd_row.get("ColNo", 0)

            self._grid_layout.addWidget(grid, row_no, col_no)

    # ------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
