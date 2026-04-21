
from PySide6.QtWidgets import QTableView

class GrdPY(QTableView):
    def __init__(self):
        super().__init__()
        self.open_with_cod_sys_frm_grd = None

    def SaveOperation(self):
        print('Save grid', self.open_with_cod_sys_frm_grd)

    def ExtraButtonOperation(self, cod):
        print('Extra button', cod)
