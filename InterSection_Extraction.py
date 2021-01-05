from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from .resources import *
# Import the code for the dialog
from .Intersection_Extraction2 import Intersection_Extraction2

import os
import os.path
import sys
import codecs

QString = str

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class InterSection_Extraction:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'InterSection_Extraction_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.actions = []
        self.menu = u'InterSection_Extraction'
        self.toolbar = self.iface.addToolBar(u'InterSection_Extraction')
        self.toolbar.setObjectName(u'InterSection_Extraction')

    def tr(self, message):
        return QCoreApplication.translate('Intersection_Extraction', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action

    def initGui(self):
        self.win = self.iface.mainWindow()
        icon_path = ':/plugins/Sample/icon.png'
        #メニュー設定
        self.add_action(
            icon_path=None,
            text=u"Intersection_Extraction",
            callback=self.IS_Extraction,
            parent=self.win)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                u'Sample',
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    #Menu02メニュークリック
    def IS_Extraction(self):
        #Intersection_Extraction読み込み
        self.is_Extraction = Intersection_Extraction2(self.iface)
        #Intersection_ExtractionDialog表示
        self.is_Extraction.dlg.show()

    def run(self):
        pass