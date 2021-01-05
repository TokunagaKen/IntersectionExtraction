from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from qgis.core import *
from qgis.gui import *

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, 
    QAction, QFileDialog, QApplication, QWidget, QProgressBar, QMessageBox,
    QPushButton, QLabel)

from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd
import numpy as np
import csv
import copy
from math import *


#Intersection_ExtractionDialog読み込み
from .Intersection_ExtractionDialog import Intersection_ExtractionDialog

QString = str

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class Intersection_Extraction2(QMainWindow, QWidget):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        #Intersection_ExtractionDialog読み込み
        self.dlg = Intersection_ExtractionDialog()
        #ボタン設定
        self.dlg.pushButton_go.clicked.connect(self.dlg_add)
        self.dlg.pushButton_cancel.clicked.connect(self.dlg_cancel)

    #キャンセルクリック
    def dlg_cancel(self):
        #Intersection_ExtractionDialog非表示
        self.dlg.hide()

    #OKクリック
    def dlg_add(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home', "Excel(*.xlsx)")
        self.Old_ISOrginFile = pd.read_excel(fname[0])
        # QMessageBox.information(None, u'ウィンドウ名', fname[0])

        # ローディングゲージの作成コード1
        self.lbl = QLabel('重複しているデータの除去進行率', self)
        self.lbl.setGeometry(QtCore.QRect(30, 10, 241, 16))
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.lbl2 = QLabel('クラスタリングによる交差点抽出の進行率', self)
        self.lbl2.setGeometry(QtCore.QRect(30, 80, 241, 16))
        self.pbar2 = QProgressBar(self)
        self.pbar2.setGeometry(30, 110, 200, 25)
        self.NoDeplicateFile_step = 0
        self.CreateIS_step = 0
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QProgressBar')
        self.show()
        self.pbar.setValue(self.NoDeplicateFile_step)
        self.pbar2.setValue(self.CreateIS_step)
        QMessageBox.information(None, u'ウィンドウ名', '処理を開始します\n(処理の進捗状況を確認したい場合は、以降PCに触れないでください)')

        self.ISOrginFile = pd.DataFrame(columns = ["X", "Y", "id_1", "id_2"])
        for ab in range(len(self.Old_ISOrginFile)):
            flag = False
            for cd in range(len(self.ISOrginFile)):
                if (self.Old_ISOrginFile.iat[ab,0] == self.ISOrginFile.iat[cd,0] and self.Old_ISOrginFile.iat[ab,1] == self.ISOrginFile.iat[cd,1]):
                    flag = True
                    break
            if not(flag):
                self.ISOrginFile = self.ISOrginFile.append({'X' : self.Old_ISOrginFile.iat[ab,0], 'Y' : self.Old_ISOrginFile.iat[ab,1],
                                                            'id_1' : self.Old_ISOrginFile.iat[ab,2], 'id_2' : self.Old_ISOrginFile.iat[ab,3]}, ignore_index=True)
                self.NoDeplicateFile_step = int(100 - (((len(self.Old_ISOrginFile) - len(self.ISOrginFile)) / len(self.Old_ISOrginFile)) * 100))
                self.pbar.setValue(self.NoDeplicateFile_step)
        self.NoDeplicateFile_step = 100
        self.pbar.setValue(self.NoDeplicateFile_step) 

        SaveR_ISList = []
        Save_ISGroup = []
        Residual_ISList = []
        AveragePosList = []
        Start_Residual_ISList = 0

        while(True):
            if(len(SaveR_ISList) == 0):
                Residual_ISList = []
                for i in range(len(self.ISOrginFile)):
                    Residual_ISList.append([self.ISOrginFile.iat[i, 0], self.ISOrginFile.iat[i, 1]])
                Start_Residual_ISList = len(Residual_ISList)
            else:
                Residual_ISList = copy.copy(SaveR_ISList)

            Is_0DivisionError = False

            while(len(Residual_ISList) != 0):
                for i in range(len(self.ISOrginFile)):
                    if not [self.ISOrginFile.iat[i, 0], self.ISOrginFile.iat[i, 1]] in Residual_ISList:
                        continue
                    ISGroup = []
                    ISGroup.append([self.ISOrginFile.iat[i, 0], self.ISOrginFile.iat[i, 1]])
                    Residual_ISList.remove([self.ISOrginFile.iat[i, 0], self.ISOrginFile.iat[i, 1]])
                    ISGroup, Residual_ISList, Is_0DivisionError = self.kousakinnrinn(ISGroup, Residual_ISList,
                                                                                    self.ISOrginFile.iat[i, 0], self.ISOrginFile.iat[i, 1],
                                                                                    self.ISOrginFile.iat[i, 2], self.ISOrginFile.iat[i, 3],
                                                                                    Is_0DivisionError)
                    if(Is_0DivisionError):
                        SaveR_ISList[len(SaveR_ISList):len(SaveR_ISList)] = ISGroup
                        SaveR_ISList = copy.copy(Residual_ISList)
                        break
                    Save_ISGroup.append(ISGroup)
                    SaveR_ISList = copy.copy(Residual_ISList)
                    self.CreateIS_step = int(((Start_Residual_ISList-len(Residual_ISList))/Start_Residual_ISList) * 100)
                    self.pbar2.setValue(self.CreateIS_step)
                if(Is_0DivisionError):
                    break
            if(Is_0DivisionError == False):
                break
        
        AveragePosList  = self.AveragePosCalulation(Save_ISGroup)
        self.CreateAvePosCsvFile(AveragePosList)
        QMessageBox.information(None, u'ウィンドウ名', '実行完了')

    def kousakinnrinn(self, _ISGroup, _Residual_ISList, x, y, id1, id2, _Is_0DivisionError):
        for j in range(len(self.ISOrginFile)):
            if not [self.ISOrginFile.iat[j,0], self.ISOrginFile.iat[j,1]] in _Residual_ISList:
                continue
            try: kyori = self.CAL_RHO(y, x, self.ISOrginFile.iat[j,1], self.ISOrginFile.iat[j,0])
            except ZeroDivisionError:
                _Residual_ISList.remove([self.ISOrginFile.iat[j, 0], self.ISOrginFile.iat[j, 1]])
                drop_index = self.ISOrginFile.index[(self.ISOrginFile['id_1'] == self.ISOrginFile.iat[j,2]) & (self.ISOrginFile['id_2'] == self.ISOrginFile.iat[j,3])]
                self.ISOrginFile.drop(drop_index, inplace = True)
                return _ISGroup, _Residual_ISList, True
            if(kyori*1000 < 14.0):
                _Residual_ISList.remove([self.ISOrginFile.iat[j,0], self.ISOrginFile.iat[j,1]])
                _ISGroup.append([self.ISOrginFile.iat[j,0], self.ISOrginFile.iat[j,1]])       
                _ISGroup, _Residual_ISList, _Is_0DivisionError = self.kousakinnrinn(_ISGroup, _Residual_ISList, 
                                                                self.ISOrginFile.iat[j,0], self.ISOrginFile.iat[j,1], 
                                                                self.ISOrginFile.iat[j,2], self.ISOrginFile.iat[j,3],
                                                                _Is_0DivisionError)
                if(_Is_0DivisionError):
                    return _ISGroup, _Residual_ISList, _Is_0DivisionError 
        return  _ISGroup, _Residual_ISList, _Is_0DivisionError

    def CAL_PHI(self, ra,rb,lat):
        return atan(rb/ra*tan(lat))
    
    def CAL_RHO(self, Lat_A,Lon_A,Lat_B,Lon_B):#緯度，経度
        ra=6378.140  # 赤道半径
        rb=6356.755  # 極半径
        F=(ra-rb)/ra # 地球の平坦化
        rad_lat_A=radians(Lat_A) # radianに変換
        rad_lon_A=radians(Lon_A) # //
        rad_lat_B=radians(Lat_B) # //
        rad_lon_B=radians(Lon_B) # //
        pA=self.CAL_PHI(ra,rb,rad_lat_A) # 逆余弦定理
        pB=self.CAL_PHI(ra,rb,rad_lat_B) # //
        xx=acos(sin(pA)*sin(pB)+cos(pA)*cos(pB)*cos(rad_lon_A-rad_lon_B))
        c1=(sin(xx)-xx)*(sin(pA)+sin(pB))**2/cos(xx/2)**2
        c2=(sin(xx)+xx)*(sin(pA)-sin(pB))**2/sin(xx/2)**2
        dr=F/8*(c1-c2)
        rho=ra*(xx+dr)
        return rho

    def AveragePosCalulation(self, _Save_ISGroup):
        AvePosList = []
        for i in range(len(_Save_ISGroup)):
            SumPosX = SumPosY = 0
            count = 0
            for j in range(len(_Save_ISGroup[i])):
                SumPosX += _Save_ISGroup[i][j][0]
                SumPosY += _Save_ISGroup[i][j][1]
                count += 1
            AvePosList.append([SumPosX/count, SumPosY/count])
        return AvePosList

    def CreateAvePosCsvFile(self, _AveragePosList):
        file = open("%USERPROFILE%/Documents/AveragePointData_From_QGIS3_InterSection_Extraction.csv", "w", newline="")
        w = csv.writer(file, skipinitialspace=True)
        w.writerow(["", "X", "Y"])
        for i in range(len(_AveragePosList)):
            _AveragePosList[i].insert(0, i)
            w.writerow(_AveragePosList[i])
 
        file.close()
        return

   