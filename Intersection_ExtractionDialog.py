from PyQt5 import uic, QtWidgets, QtCore

#Ui_Intersection_ExtractionBase読み込み
from .Intersection_ExtractionBase import Ui_Intersection_ExtractionBase

class Intersection_ExtractionDialog(QtWidgets.QDialog, Ui_Intersection_ExtractionBase):
    def __init__(self, parent=None):
        super(Intersection_ExtractionDialog, self).__init__(parent)
        self.setupUi(self)