"""LASDiA Controller
"""


from __future__ import (absolute_import, division, print_function, unicode_literals)
import six

import sys
import os
from os import path
import subprocess

import numpy as np

import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from modules import Formalism
from modules import Geometry
from modules import IgorFunctions
from modules import KaplowMethod
from modules import MainFunctions
from modules import Minimization
from modules import Optimization
from modules import Utility
from modules import UtilityAnalysis

# from modules import myMassEl_v16_code

from modules import LASDiAGUI

# class MyPopup(QWidget):
    # def __init__(self):
        # QWidget.__init__(self)


class LASDiA(QtWidgets.QMainWindow, LASDiAGUI.Ui_LASDiAGUI):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.ui = LASDiAGUI.Ui_LASDiAGUI()
        self.ui.setupUi(self)
        
        # Set the variable
        self.dirpath = None
        self.Q = None
        self.I_Q = None
        self.Qbkg = None
        self.Ibkg_Q = None
        self.orgQ = None
        self.orgI_Q = None
        self.orgQbkg = None
        self.orgIbkg_Q = None
        self.SsmoothDamp_Q = None
        self.elementList = None
        self.elementParameters = None
        self.Ztot = None
        self.fe_Q = None
        self.r = None
        self.F_r = None
        self.Sinf = None
        self.i_Q = None
        self.Qi_Q = None
        # self.rho0 = None
        self.Iincoh_Q = None
        self.J_Q = None
        self.dampingFunct = None
        self.molecule = "Ar"
        
        self.XYZFilePath = None
        
        # Set the buttons
        self.ui.dataPath.clicked.connect(self.importPath)
        self.ui.importData.clicked.connect(self.import_data)
        self.ui.importBkg.clicked.connect(self.import_bkg)
        
        self.ui.dataInterpolation.clicked.connect(self.interpolation)
        
        self.ui.sampleComposition.clicked.connect(self.setComposition)
        
        self.ui.calcSQ.clicked.connect(self.SQ)
        self.ui.calcFr.clicked.connect(self.Fr)
        self.ui.optimize.clicked.connect(self.Optimization)
        #self.ui.Minimization.clicked.connect(self.calcMinimization)
        self.ui.importXYZFile.clicked.connect(self.import_XYZFile)
        # self.ui.removePeaksData.clicked.connect(self.remove_PeaksData)
        # self.ui.removePeaksBkg.clicked.connect(self.remove_PeaksBkg)
        # self.ui.interpolationData.clicked.connect(self.interpolation_Data)
        # self.ui.interpolationBkg.clicked.connect(self.interpolation_Bkg)

        self.ui.plotMiddleButton.clicked.connect(self.plotMiddle)
        self.ui.plotBottomButton.clicked.connect(self.plotBottom)
        
    #---------------------------------------------------------  

    def importPath(self):
        """Function to load and plot the data file"""
        
        self.dirpath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Open directory",
            r"..\data\cea_files\Ar", QtWidgets.QFileDialog.ShowDirsOnly))
            # expanduser("~"), QtWidgets.QFileDialog.ShowDirsOnly))
        
        self.ui.dataPathName.setPlainText(self.dirpath)
        
    #---------------------------------------------------------
    
    def import_data(self):
        """Function to load and plot the data file"""
        
        # commented just for testing
        # if self.ui.dataFileName.toPlainText() == "":
            # path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Data File",
                # r"../data/cea_files/Ar", "Data File(*chi *xy)")
        # else:
            # path = self.dirpath + "/" + self.ui.dataFileName.toPlainText()
            # # if self.ui.dataPathName.toPlainText() == "":
                # # self.dirpath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Open directory",
                    # # r"..\data\cea_files\Ar", QtWidgets.QFileDialog.ShowDirsOnly))
            # # else:
                # # self.dirpath = self.ui.dataPathName.toPlainText()
                # # path = self.dirpath + "/" + self.ui.dataFileName.toPlainText()
        
        
        path = r"../data/cea_files/Ar/HT2_034T++_rem.chi"
        pathDir, fileName = os.path.split(path)
        self.ui.dataPathName.setPlainText(pathDir)
        self.ui.dataFileName.setPlainText(fileName)
        
        self.Q, self.I_Q = Utility.read_file(path)
        self.orgQ = self.Q
        self.orgI_Q = self.I_Q
        
        self.ui.rawDataPlot.canvas.ax.plot(self.Q, self.I_Q, "b", label="Data")
        self.ui.rawDataPlot.canvas.ax.legend()
        self.ui.rawDataPlot.canvas.draw()
        
        
    #---------------------------------------------------------

    def import_bkg(self):
        """Function to load and plot the bkg file"""
        
        # commented just for testing
        # if self.ui.bkgFileName.toPlainText() == "":
            # path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Bkg File",
                # r"../data/cea_files/Ar", "Data File(*chi *xy)")
        # else:
            # path = self.dirpath + "/" + self.ui.bkgFileName.toPlainText()
        
        path = r"../data/cea_files/Ar/HT2_036T++_rem.chi"
        pathDir, fileName = os.path.split(path)
        self.ui.dataPathName.setPlainText(pathDir)
        self.ui.bkgFileName.setPlainText(fileName)
        
        self.Qbkg, self.Ibkg_Q = Utility.read_file(path)
        self.orgQbkg = self.Qbkg
        self.orgIbkg_Q = self.Ibkg_Q
        path = ""
        
        self.ui.rawDataPlot.canvas.ax.plot(self.Qbkg, self.Ibkg_Q, "g--", label="Bkg")
        self.ui.rawDataPlot.canvas.ax.legend()
        self.ui.rawDataPlot.canvas.draw()

    #---------------------------------------------------------

    def interpolation(self):
        """Function to interpolate data"""
        
        self.Q, self.I_Q = UtilityAnalysis.data_interpolation(self.orgQ, self.orgI_Q, 
            self.ui.minQ.value(), self.ui.maxQ.value(),
            self.ui.interpolationPoints.value())

        self.Qbkg, self.Ibkg_Q = UtilityAnalysis.data_interpolation(self.orgQbkg, self.orgIbkg_Q, 
            self.ui.minQ.value(), self.ui.maxQ.value(),
            self.ui.interpolationPoints.value())
        
        self.ui.rawDataPlot.canvas.ax.lines.pop(0)
        self.ui.rawDataPlot.canvas.ax.lines.pop(0)
        
        self.ui.rawDataPlot.canvas.ax.plot(self.Q, self.I_Q, "b", label="Data")
        self.ui.rawDataPlot.canvas.ax.legend()
        self.ui.rawDataPlot.canvas.draw()
        
        self.ui.rawDataPlot.canvas.ax.plot(self.Qbkg, self.Ibkg_Q, "g--", label="Bkg")
        self.ui.rawDataPlot.canvas.ax.legend()
        self.ui.rawDataPlot.canvas.draw()

    #---------------------------------------------------------
    
    def setComposition(self):
        """Function to set the sample composition"""
        
        # os.system("python.exe ./modules/myMassEl_v16_code.py")
        # form = myMassEl_v16_code.Calculate()
        # form.show()
        # command = ["python.exe", "./modules/myMassEl_v16_code.py"]
        
        command = [sys.executable, "./modules/myMassEl_v16_code.py"]
        p = subprocess.Popen(command, stdout=subprocess.PIPE)
        self.molecule = p.stdout.read().decode('ascii')
        # print("molecule", self.molecule)
        # elementList = Utility.molToElemList(self.molecule)
        # print(elementList)
        self.ui.composition.setPlainText(self.molecule)

    #---------------------------------------------------------
    
    def import_XYZFile(self):
        """Function to load and plot the bkg file"""
        
        self.XYZFilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load XYZ File",
            r"./", "Data File(*xyz)")
        
        self.ui.xyzFileName.setPlainText(self.XYZFilePath)

    #---------------------------------------------------------

    def plotMiddle(self):
        """Function to plot the graph on the Middle Canvas"""

        self.ui.factorPlot.canvas.ax.cla()
        self.ui.factorPlot.canvas.ax.grid(True)

        self.elementList = Utility.molToElemList(self.molecule)
        self.elementParameters = Utility.read_parameters(self.elementList, 
            "./elementParameters.txt")

        if self.ui.formFactorCheck.isChecked():
            # print("test fe check")
            self.Q, self.I_Q, self.Qbkg, self.Ibkg_Q = UtilityAnalysis.check_data_length(self.Q,
                self.I_Q, self.Qbkg, self.Ibkg_Q, self.ui.minQ.value(), self.ui.maxQ.value())
            self.fe_Q, self.Ztot = MainFunctions.calc_eeff(self.elementList, self.Q,
                self.elementParameters)

            self.ui.factorPlot.canvas.ax.plot(self.Q, self.fe_Q, label=r"$f_e(Q)$")
            self.ui.factorPlot.canvas.ax.legend()
            self.ui.factorPlot.canvas.draw()
        # else:
        #     # print("test unchecked")
        #     self.ui.factorPlot.canvas.ax.lines.pop(0)
        #     self.ui.factorPlot.canvas.draw()
            
        if self.ui.SQCheck.isChecked():
            S_Q = self.SQ()            
            self.ui.factorPlot.canvas.ax.plot(self.Q, S_Q, label=r"$S(Q)$")
            self.ui.factorPlot.canvas.ax.legend()
            self.ui.factorPlot.canvas.draw()

        if self.ui.incohCheck.isChecked():
            self.Iincoh_Q = MainFunctions.calc_Iincoh(self.elementList, self.Q,
                self.elementParameters)
    
            self.ui.factorPlot.canvas.ax.plot(self.Q, self.Iincoh_Q, label=r"$I_{incoh}(Q)$")
            self.ui.factorPlot.canvas.ax.legend()
            self.ui.factorPlot.canvas.draw()

        if self.ui.QiQCheck.isChecked():
            self.Sinf = MainFunctions.calc_Sinf(self.elementList, self.fe_Q, self.Q,
                self.Ztot, self.elementParameters)
            self.i_Q = MainFunctions.calc_iQ(S_Q, self.Sinf)
            # self.r = MainFunctions.calc_r(self.Q)
            Qi_Q = self.Q*self.i_Q

            self.ui.factorPlot.canvas.ax.plot(self.Q, Qi_Q, label=r"$Qi(Q)$")
            self.ui.factorPlot.canvas.ax.legend()
            self.ui.factorPlot.canvas.draw()

    #---------------------------------------------------------

    def plotBottom(self):
        """Function to plot the graph on the Middle Canvas"""

        self.ui.distfuncPlot.canvas.ax.cla()
        self.ui.distfuncPlot.canvas.ax.grid(True)

        if self.ui.FrCheck.isChecked():
            self.r, self.F_r = self.Fr()

            self.ui.distfuncPlot.canvas.ax.plot(self.r, self.F_r, label=r"$F(r)$")
            self.ui.distfuncPlot.canvas.ax.legend()
            self.ui.distfuncPlot.canvas.draw()
            
        if self.ui.grCheck.isChecked():
            g_r = 1 + self.F_r / (4 * np.pi * self.r * self.ui.densityValue.value())
            # print(g_r)

            self.ui.distfuncPlot.canvas.ax.plot(self.r, g_r, label=r"$g(r)$")
            self.ui.distfuncPlot.canvas.ax.legend()
            self.ui.distfuncPlot.canvas.draw()

    #---------------------------------------------------------

    def SQ(self):
        """Function to calculate and plot the structure factor S(Q)"""
        
        self.elementList = Utility.molToElemList(self.molecule)
        # self.elementList = Utility.molToElemList("Ar")
        self.elementParameters = Utility.read_parameters(self.elementList, 
            "./elementParameters.txt")
        
        # print(elementList)
        # print(elementParameters)

        self.Q, self.I_Q, self.Qbkg, self.Ibkg_Q = UtilityAnalysis.check_data_length(self.Q,
            self.I_Q, self.Qbkg, self.Ibkg_Q, self.ui.minQ.value(), self.ui.maxQ.value())
        
        two_theta = UtilityAnalysis.Qto2theta(self.Q)
        absCorrFactor = Geometry.calcAbsCorrection(self.ui.absLength.value(),
            two_theta, self.ui.dacThickness.value(), self.ui.dacAngle.value())
        self.I_Q = self.I_Q/absCorrFactor
        self.Ibkg_Q = self.Ibkg_Q/absCorrFactor

        self.fe_Q, self.Ztot = MainFunctions.calc_eeff(self.elementList, self.Q,
            self.elementParameters)
        self.Iincoh_Q = MainFunctions.calc_Iincoh(self.elementList, self.Q,
            self.elementParameters)
        self.J_Q = MainFunctions.calc_JQ(self.Iincoh_Q, self.Ztot, self.fe_Q)
        self.Sinf = MainFunctions.calc_Sinf(self.elementList, self.fe_Q, self.Q,
            self.Ztot, self.elementParameters)
        
        self.dampingFunct = UtilityAnalysis.calc_dampingFunction(self.Q,
            self.ui.dampingFactor.value(), self.ui.QmaxIntegrate.value(),
            self.ui.dampingFunction.currentText())
        
        Isample_Q = MainFunctions.calc_IsampleQ(self.I_Q, 
            self.ui.scaleFactorValue.value(), self.Ibkg_Q)
        alpha = MainFunctions.calc_alpha(self.J_Q[self.Q<=self.ui.QmaxIntegrate.value()],
            self.Sinf, self.Q[self.Q<=self.ui.QmaxIntegrate.value()],
            Isample_Q[self.Q<=self.ui.QmaxIntegrate.value()],
            self.fe_Q[self.Q<=self.ui.QmaxIntegrate.value()], self.Ztot,
            self.ui.densityValue.value())
        Icoh_Q = MainFunctions.calc_Icoh(alpha, Isample_Q, self.Iincoh_Q)
        
        S_Q = MainFunctions.calc_SQ(Icoh_Q, self.Ztot, self.fe_Q, self.Sinf,
            self.Q, self.ui.minQ.value(), self.ui.QmaxIntegrate.value(),
            self.ui.maxQ.value())
        Ssmooth_Q = UtilityAnalysis.calc_SQsmoothing(self.Q, S_Q, self.Sinf,
            self.ui.smoothingFactor.value(), self.ui.minQ.value(),
            self.ui.QmaxIntegrate.value(), self.ui.maxQ.value())
        self.SsmoothDamp_Q = UtilityAnalysis.calc_SQdamp(Ssmooth_Q, self.Sinf,
            self.dampingFunct)
        
        # self.ui.factorPlot.canvas.ax.plot(self.Q, self.SsmoothDamp_Q, "b", label=r"$S(Q)$")
        # self.ui.factorPlot.canvas.ax.legend()
        # self.ui.factorPlot.canvas.draw()

        return self.SsmoothDamp_Q

    #---------------------------------------------------------

    def Fr(self):
        """Function to calculte and plot F(r)"""
        
        self.i_Q = MainFunctions.calc_iQ(self.SsmoothDamp_Q, self.Sinf)
        # self.r = MainFunctions.calc_r(self.Q)
        Qi_Q = self.Q*self.i_Q 
        self.r, self.F_r = MainFunctions.calc_Fr(self.Q[self.Q<=self.ui.QmaxIntegrate.value()],
            Qi_Q[self.Q<=self.ui.QmaxIntegrate.value()])
        
        # self.ui.distfuncPlot.canvas.ax.plot(self.r, self.F_r, "b", label=r"$F(r)$")
        # self.ui.distfuncPlot.canvas.ax.legend()
        # self.ui.distfuncPlot.canvas.draw()

        return (self.r, self.F_r)
    
    #---------------------------------------------------------

    def Optimization(self):
        """Function to optimize and plot F(r)"""
        
        #-------------------Intra-molecular components-----------------------------

        # numAtoms, element, x, y, z = Utility.read_xyz_file(self.XYZFilePath)
        numAtoms, element, x, y, z = Utility.read_xyz_file("/Users/ciccio/work/ID27/LASDiA/xyzFiles/Ar.xyz")

        iintra_Q = Optimization.calc_iintra(self.Q, self.fe_Q, self.Ztot,
            self.ui.QmaxIntegrate.value(),
            self.ui.maxQ.value(), self.elementList, element, x, y, z, self.elementParameters)
        iintradamp_Q = UtilityAnalysis.calc_iintradamp(iintra_Q, self.dampingFunct)
        Qiintradamp_Q = self.Q*iintradamp_Q
        rintra, Fintra_r = MainFunctions.calc_Fr(self.Q[self.Q<=self.ui.QmaxIntegrate.value()], 
            Qiintradamp_Q[self.Q<=self.ui.QmaxIntegrate.value()])

        scaleFactor = self.ui.scaleFactorValue.value()
        density0 = self.ui.densityValue.value()

        # ----------------------First scale minimization---------------------------

        scaleStep = 0.05

        # sth = 0.008
        # s0th = 0.006
        sth = 0.0
        s0th = 0.0
        phi_matrix = 0.0
        thickness_sampling = 0.0

        scaleFactor = Minimization.OptimizeScale(self.Q, self.I_Q, self.Ibkg_Q, 
            self.J_Q, self.Iincoh_Q,
            self.fe_Q, self.ui.maxQ.value(), self.ui.minQ.value(), 
            self.ui.QmaxIntegrate.value(),
            self.Ztot,
            density0, scaleFactor, self.Sinf, self.ui.smoothingFactor.value(),
            self.ui.rmin.value(),
            self.dampingFunct, Fintra_r, self.ui.iterations.value(), scaleStep,
            sth, s0th, thickness_sampling, phi_matrix, "n")

        # ----------------------First density minimization-------------------------

        densityStep = density0/50
        densityStepEnd = density0/250

        density = Minimization.OptimizeDensity(self.Q, self.I_Q, self.Ibkg_Q, 
            self.J_Q, self.Iincoh_Q,
            self.fe_Q, self.ui.maxQ.value(), self.ui.minQ.value(), 
            self.ui.QmaxIntegrate.value(),
            self.Ztot, 
            density0, scaleFactor, self.Sinf, self.ui.smoothingFactor.value(),
            self.ui.rmin.value(),
            self.dampingFunct, Fintra_r, self.ui.iterations.value(), densityStep,
            densityStepEnd, sth, s0th, thickness_sampling, phi_matrix, "n")

        # print("density0, density", density0, density)
        numLoopIteration = 0

        while 1:
            if np.abs(density-density0) > density/25:
                # print("First")
                scaleStep = 0.006
                densityStep = density/10
                WSamplestep=0.0008
                WRefstep=0.0008
            elif np.abs(density-density0) > density/75:
                # print("Second")
                scaleStep = 0.0006
                densityStep = density/100
                WSamplestep=0.0002
                WRefstep=0.0002
            else:
                # print("Third")
                scaleStep = 0.00006
                densityStep = density/1000
                WSamplestep=0.0001
                WRefstep=0.0001
            
            scaleFactor = Minimization.OptimizeScale(self.Q, self.I_Q, self.Ibkg_Q, 
                self.J_Q, self.Iincoh_Q,
                self.fe_Q, self.ui.maxQ.value(), self.ui.minQ.value(), 
                self.ui.QmaxIntegrate.value(),
                self.Ztot,
                density, scaleFactor, self.Sinf, self.ui.smoothingFactor.value(),
                self.ui.rmin.value(),
                self.dampingFunct, Fintra_r, self.ui.iterations.value(), scaleStep,
                sth, s0th, thickness_sampling, phi_matrix, "n")

            density0=density

            density = Minimization.OptimizeDensity(self.Q, self.I_Q, self.Ibkg_Q, 
                self.J_Q, self.Iincoh_Q,
                self.fe_Q, self.ui.maxQ.value(), self.ui.minQ.value(), 
                self.ui.QmaxIntegrate.value(),
                self.Ztot, 
                density0, scaleFactor, self.Sinf, self.ui.smoothingFactor.value(),
                self.ui.rmin.value(),
                self.dampingFunct, Fintra_r, self.ui.iterations.value(), densityStep,
                density/250, sth, s0th, thickness_sampling, phi_matrix, "n")

            numLoopIteration += 1
            # print("numLoopIteration", numLoopIteration, scaleFactor, density)
            if (np.abs(density-density0) > np.abs(density/2500)) and (numLoopIteration <= 30):
               continue
            else:
                break
               
        # print("final scale", scaleFactor, "final density", density)
        
        self.ui.scaleFactorValue.setValue(scaleFactor)
        self.ui.densityValue.setValue(density)

        Isample_Q = MainFunctions.calc_IsampleQ(self.I_Q, scaleFactor, self.Ibkg_Q)
        alpha = MainFunctions.calc_alpha(self.J_Q[self.Q<=self.ui.QmaxIntegrate.value()],
            self.Sinf, 
            self.Q[self.Q<=self.ui.QmaxIntegrate.value()],
            Isample_Q[self.Q<=self.ui.QmaxIntegrate.value()], 
            self.fe_Q[self.Q<=self.ui.QmaxIntegrate.value()], self.Ztot, density)
        Icoh_Q = MainFunctions.calc_Icoh(alpha, Isample_Q, self.Iincoh_Q)

        S_Q = MainFunctions.calc_SQ(Icoh_Q, self.Ztot, self.fe_Q, self.Sinf, self.Q,
            self.ui.minQ.value(), 
            self.ui.QmaxIntegrate.value(), self.ui.maxQ.value())

        Ssmooth_Q = UtilityAnalysis.calc_SQsmoothing(self.Q, S_Q, self.Sinf, 
            self.ui.smoothingFactor.value(), self.ui.minQ.value(), 
            self.ui.QmaxIntegrate.value(), self.ui.maxQ.value())

        SsmoothDamp_Q = UtilityAnalysis.calc_SQdamp(Ssmooth_Q, self.Sinf,
            self.dampingFunct)

        i_Q = MainFunctions.calc_iQ(SsmoothDamp_Q, self.Sinf)
        
        Qi_Q = self.Q*i_Q
        r, F_r = MainFunctions.calc_Fr(self.Q[self.Q<=self.ui.QmaxIntegrate.value()], 
            Qi_Q[self.Q<=self.ui.QmaxIntegrate.value()])
        Fopt_r, deltaFopt_r = Optimization.calc_optimize_Fr(self.ui.iterations.value(), 
            F_r, Fintra_r, density, i_Q[self.Q<=self.ui.QmaxIntegrate.value()], 
            self.Q[self.Q<=self.ui.QmaxIntegrate.value()],
            self.Sinf, self.J_Q[self.Q<=self.ui.QmaxIntegrate.value()], r, 
            self.ui.rmin.value(), "n")
        
        Scorr_Q = MainFunctions.calc_SQCorr(Fopt_r, r, self.Q, self.Sinf)

        self.ui.distfuncPlot.canvas.ax.plot(r, Fopt_r, "g", label=r"$F_{opt}(r)$")
        self.ui.distfuncPlot.canvas.ax.legend()
        self.ui.distfuncPlot.canvas.draw()
        
        self.ui.factorPlot.canvas.ax.plot(self.Q, Scorr_Q, "g", label=r"$S_{opt}(Q)$")
        self.ui.factorPlot.canvas.ax.legend()
        self.ui.factorPlot.canvas.draw()        

        # Fintra_r = np.zeros(self.r.size)

        # elementList = Utility.molToelemList("Ar")
        # elementParameters = Utility.read_parameters(elementList, "./elementParameters.txt")
        # numAtoms, element, x, y, z = Utility.read_xyz_file(self.XYZFilePath)
        
        
        # iintra_Q = Optimization.calc_iintra(self.Q, self.fe_Q, self.Ztot, self.ui.QmaxIntegrate.value(), 
        #     self.ui.maxQ.value(), elementList, element, x, y, z, elementParameters)
        # iintradamp_Q = UtilityAnalysis.calc_iintradamp(iintra_Q, self.Q, self.ui.QmaxIntegrate.value(), 
        #     self.dampingFunct)
        # # r = MainFunctions.calc_r(self.Q)
        # Fintra_r = MainFunctions.calc_Fr2(self.r, self.Q[self.Q<=self.ui.QmaxIntegrate.value()], 
        #     iintradamp_Q[self.Q<=self.ui.QmaxIntegrate.value()])
        
        # F_rIt, deltaF_rIt = Optimization.calc_optimize_Fr(self.ui.iterations.value(), self.F_r, \
        #     Fintra_r, self.ui.density.value(), self.i_Q[self.Q<=self.ui.QmaxIntegrate.value()], \
        #     self.Q[self.Q<=self.ui.QmaxIntegrate.value()], self.Sinf, \
        #     self.J_Q[self.Q<=self.ui.QmaxIntegrate.value()], self.r, self.ui.rmin.value(), "n")
        
        # r, iintradamp_Q, Fintra_r = Optimization.calc_intraComponent(self.Q, self.fe_Q, self.Ztot, \
            # self.ui.QmaxIntegrate.value(), self.ui.maxQ.value(), elementList, element, \
            # x, y, z, elementParameters, self.ui.dampingFactor.value())
        
        # density, scaleFactor = Minimization.chi2_minimization(self.ui.scaleFactor.value(), 
            # self.Q, self.I_Q, self.Ibkg_Q, 
            # self.J_Q, self.fe_Q, self.Iincoh_Q, self.Sinf, self.Ztot,
            # self.ui.density.value(), Fintra_r, self.r, self.ui.minQ.value(), self.ui.QmaxIntegrate.value(), variables.maxQ, 
            # variables.smoothingFactor, variables.dampingFactor, variables.iteration, variables.rmin)
        
        # scaleStep = 0.05
        # densityStep = 0.025
        # numSample = 23
        # numLoopIteration = 0
        
        # # plt.ion()
        # # figure, ax = plt.subplots()
        
        # scaleFactor = self.ui.scaleFactor.value()
        # density = self.ui.density.value()
        
        # # print("density ", density, " Scale Factor ", scaleFactor)
        
        # while True:
            # self.ui.chi2_plot.canvas.ax.cla()
            # self.ui.chi2_plot.canvas.ax.grid(True)
            # scaleArray = UtilityAnalysis.make_array_loop(scaleFactor, scaleStep, numSample)
            
            # chi2Array = np.zeros(numSample)
            
            # self.ui.chi2_plot.canvas.ax.set_xlabel("Scale")
            # self.ui.chi2_plot.canvas.ax.relim()
            # self.ui.chi2_plot.canvas.ax.autoscale_view()
            # for i in range(len(scaleArray)):
                # chi2Array[i], SsmoothDamp_Q, F_r, Fopt_r = KaplowMethod.Kaplow_method(self.Q, self.I_Q,
                    # self.Ibkg_Q, self.J_Q, self.fe_Q, self.Iincoh_Q, self.Sinf, self.Ztot, scaleArray[i], density, Fintra_r, self.r,
                    # self.ui.minQ.value(), self.ui.QmaxIntegrate.value(), self.ui.maxQ.value(), self.ui.smoothingFactor.value(),
                    # self.ui.dampingFactor.value(), self.ui.iterations.value(), self.ui.rmin.value())
                
                # self.ui.chi2_plot.canvas.ax.scatter(scaleArray[i], chi2Array[i])
                # self.ui.chi2_plot.canvas.draw()
            
            # xfit, yfit, scaleFactor = Minimization.chi2_fit(scaleArray, chi2Array)
            # self.ui.chi2_plot.canvas.ax.plot(xfit, yfit)
            # self.ui.chi2_plot.canvas.draw()
            
            # self.ui.chi2_plot.canvas.ax.cla()
            # self.ui.chi2_plot.canvas.ax.grid(True)

            # density0 = density
            # densityArray = UtilityAnalysis.make_array_loop(density, densityStep, numSample)
            # chi2Array = np.zeros(numSample)
            
            # self.ui.chi2_plot.canvas.ax.set_xlabel("Density")
            # self.ui.chi2_plot.canvas.ax.relim()
            # self.ui.chi2_plot.canvas.ax.autoscale_view()
            # for i in range(len(densityArray)):
                # chi2Array[i], SsmoothDamp_Q, F_r, Fopt_r = KaplowMethod.Kaplow_method(self.Q, self.I_Q,
                    # self.Ibkg_Q, self.J_Q, self.fe_Q, self.Iincoh_Q, self.Sinf, self.Ztot, scaleFactor, densityArray[i], Fintra_r, self.r,
                    # self.ui.minQ.value(), self.ui.QmaxIntegrate.value(), self.ui.maxQ.value(), self.ui.smoothingFactor.value(),
                    # self.ui.dampingFactor.value(), self.ui.iterations.value(), self.ui.rmin.value())
                
                # self.ui.chi2_plot.canvas.ax.scatter(densityArray[i], chi2Array[i])
                # self.ui.chi2_plot.canvas.draw()
                
            
            # xfit, yfit, density = Minimization.chi2_fit(densityArray, chi2Array)
            # self.ui.chi2_plot.canvas.ax.plot(xfit, yfit)
            # self.ui.chi2_plot.canvas.draw()
            
            # if np.abs(density-density0) > density0/25:
                # scaleStep = 0.006
                # densityStep = density0/10
            # elif np.abs(density-density0) > density0/75:
                # scaleStep = 0.0006
                # densityStep = density0/100
            # else:
                # scaleStep = 0.00006
                # densityStep = density0/1000

            # numLoopIteration += 1
            # if (np.abs(density-density0) < density0/2500 or numLoopIteration > 30):
                # break
        
        # print("density ", density, " Scale Factor ", scaleFactor)
        
        # S_Q = UtilityAnalysis.S_QCalculation(self.Q, self.I_Q, self.Ibkg_Q, scaleFactor, 
            # self.J_Q, self.Sinf, self.fe_Q, self.Ztot, density, self.Iincoh_Q, 
            # self.ui.minQ.value(), self.ui.QmaxIntegrate.value(), self.ui.maxQ.value(), self.ui.smoothingFactor.value(), self.ui.dampingFactor.value())
        
        # i_Q = MainFunctions.calc_iQ(S_Q, self.Sinf)
        # F_r = MainFunctions.calc_Fr(self.r, self.Q[self.Q<=self.ui.QmaxIntegrate.value()], i_Q[self.Q<=self.ui.QmaxIntegrate.value()])
        
        # Fopt_r, deltaFopt_r = Optimization.calc_optimize_Fr(self.ui.iterations.value(), self.F_r, \
            # Fintra_r, density, i_Q[self.Q<=self.ui.QmaxIntegrate.value()], \
            # self.Q[self.Q<=self.ui.QmaxIntegrate.value()], self.Sinf, \
            # self.J_Q[self.Q<=self.ui.QmaxIntegrate.value()], self.r, self.ui.rmin.value(), "n")
            
        # Sopt_Q = MainFunctions.calc_SQCorr(Fopt_r, self.r, self.Q, self.Sinf)
            
        # # F_rIt, deltaF_rIt = Optimization.calc_optimize_Fr(self.ui.iterations.value(), self.F_r, \
            # # Fintra_r, self.ui.density.value(), self.i_Q[self.Q<=self.ui.QmaxIntegrate.value()], \
            # # self.Q[self.Q<=self.ui.QmaxIntegrate.value()], self.Sinf, \
            # # self.J_Q[self.Q<=self.ui.QmaxIntegrate.value()], self.r, self.ui.rmin.value(), "n")
        
        # Sopt_Q = MainFunctions.calc_SQCorr(F_rIt, self.r, self.Q, self.Sinf)
            
    #---------------------------------------------------------


def main():
    # app = QtWidgets.QApplication(sys.argv)
    # LASDiA = LASDiAGUI.QtWidgets.QMainWindow()
    # ui = LASDiAGUI.Ui_LASDiAGUI()
    # ui.setupUi(LASDiA)
    # LASDiA.show()
    # sys.exit(app.exec_())
    
    app = QtWidgets.QApplication(sys.argv)
    ui = LASDiA()
    ui.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
