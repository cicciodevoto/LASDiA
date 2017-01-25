# The MIT License (MIT)

# Copyright (c) 2015-2016 European Synchrotron Radiation Facility

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""LASDiA main script file.
This script is mainly used for testing the software, but it can be used to run LASDiA
in text mode.

The nomenclature and the procedures follow the article: Eggert et al. 2002 PRB, 65, 174105.

For the variables name I used this convention:
if the variable symbolizes a mathematical function, its argument is preceded by
an underscore: f(x) -> f_x
otherwise it is symbolized with just its name.
"""


from __future__ import (absolute_import, division, print_function, unicode_literals)
import six

import sys
import matplotlib.pyplot as plt
import numpy as np
import time
# from itertools import product
# from timeit import default_timer as timer
from scipy.integrate import simps
from scipy import fftpack
import math

from modules import Formalism
from modules import Geometry
from modules import IgorFunctions
from modules import KaplowMethod
from modules import MainFunctions
from modules import Minimization
from modules import Optimization
from modules import Utility
from modules import UtilityAnalysis

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget


if __name__ == "__main__":
    
    #---------------------------Files reading----------------------------------
    
    variables = Utility.read_inputFile("./inputFile.txt")
    
    elementList = Utility.molToelemList(variables.molecule)
    elementParameters = Utility.read_parameters(elementList, variables.element_params_path)
    
    path = Utility.path_xyz_file(variables.molecule)
    numAtoms, element, x, y, z = Utility.read_xyz_file(path)
    
    Q, I_Q = Utility.read_file(variables.data_file)
    Qbkg, Ibkg_Q  = Utility.read_file(variables.bkg_file)
    
    
    #--------------------Preliminary calculation-------------------------------

    Q, I_Q, Qbkg, Ibkg_Q = UtilityAnalysis.check_data_length(Q, I_Q, Qbkg, Ibkg_Q,
        variables.minQ, variables.maxQ)
    
    fe_Q, Ztot = MainFunctions.calc_eeff(elementList, Q, elementParameters)
    Iincoh_Q = MainFunctions.calc_Iincoh(elementList, Q, elementParameters)
    J_Q = MainFunctions.calc_JQ(Iincoh_Q, Ztot, fe_Q)
    Sinf, Sinf_Q = MainFunctions.calc_Sinf(elementList, fe_Q, Q, Ztot, elementParameters)
    
    dampingFunction = UtilityAnalysis.calc_dampingFunction(Q, variables.dampingFactor,
        variables.QmaxIntegrate, variables.typeFunction)

    #-------------------Intra-molecular components-----------------------------

    # iintra_Q = Optimization.calc_iintra(Q, fe_Q, Ztot, variables.QmaxIntegrate, 
        # variables.maxQ, elementList, element, x, y, z, elementParameters)
    # iintradamp_Q = UtilityAnalysis.calc_iintradamp(iintra_Q, Q, variables.QmaxIntegrate, 
        # dampingFunction)
    # r = MainFunctions.calc_r(Q)
    # Fintra_r = MainFunctions.calc_Fr(r, Q[Q<=variables.QmaxIntegrate], 
        # iintradamp_Q[Q<=variables.QmaxIntegrate])

    # ------------------------Starting minimization----------------------------

    scaleFactor = variables.scaleFactor
    density = variables.density
    
    Isample_Q = MainFunctions.calc_IsampleQ(I_Q, scaleFactor, Ibkg_Q)
    alpha = MainFunctions.calc_alpha(J_Q[Q<=variables.QmaxIntegrate], Sinf, 
        Q[Q<=variables.QmaxIntegrate], Isample_Q[Q<=variables.QmaxIntegrate],
        fe_Q[Q<=variables.QmaxIntegrate], Ztot, density)
    Icoh_Q = MainFunctions.calc_Icoh(alpha, Isample_Q, Iincoh_Q)

    S_Q = MainFunctions.calc_SQ(Icoh_Q, Ztot, fe_Q, Sinf, Q, variables.minQ, 
        variables.QmaxIntegrate, variables.maxQ)
    Ssmooth_Q = UtilityAnalysis.calc_SQsmoothing(Q, S_Q, Sinf, 
        variables.smoothingFactor, 
        variables.minQ, variables.QmaxIntegrate, variables.maxQ)
    SsmoothDamp_Q = UtilityAnalysis.calc_SQdamp(Ssmooth_Q, Sinf,
        dampingFunction)

    # Utility.plot_data(Q, S_Q, "S_Q", "Q", "S(Q)", "S(Q)", "y")

    Q, SsmoothDamp_Q = UtilityAnalysis.rebinning(Q, SsmoothDamp_Q, 0.0, 
        variables.maxQ, variables.NumPoints)
    
    i_Q = MainFunctions.calc_iQ(SsmoothDamp_Q, Sinf)
    Qi_Q = MainFunctions.calc_QiQ(Q, i_Q)
    
    
    # ----------------------------F(r) with int sum----------------------------
    
    r = MainFunctions.calc_r(Q)
    meanDeltaQ = np.mean(np.diff(Q[Q<=variables.QmaxIntegrate]))
    rQ = np.outer(r, Q[Q<=variables.QmaxIntegrate])
    sinrQ = np.sin(rQ)
    F_r = (2.0 / np.pi) * np.sum(Q[Q<=variables.QmaxIntegrate]*
        i_Q[Q<=variables.QmaxIntegrate] * sinrQ, axis=1) * meanDeltaQ
    
    # Utility.plot_data(r, F_r, "F_r", "r", "F(r)", "F(r) sum", "y")
    
    # ----------------------------F(r) with int simps--------------------------
    
    F_r2 = (2.0 / np.pi) * simps(Q[Q<=variables.QmaxIntegrate]*
        i_Q[Q<=variables.QmaxIntegrate] * sinrQ, Q[Q<=variables.QmaxIntegrate])
    
    # Utility.plot_data(r, F_r2, "F_r", "r", "F(r)", "F(r) simps", "y")
    
    # -------------------------------F(r) with FFT-----------------------------
    
    pMax, elem = UtilityAnalysis.find_nearest(Q, variables.QmaxIntegrate)
    NumPoints = 2*2*2**math.ceil(math.log(5*(pMax+1))/math.log(2))
    DelR = 2*np.pi/(np.mean(np.diff(Q))*NumPoints)
    Qi_Q = Utility.resize_zero(Q[Q<=variables.QmaxIntegrate]*i_Q[Q<=variables.QmaxIntegrate], NumPoints)
    Qi_Q[pMax+1:] = 0.0
    Q = np.arange(np.amin(Q), np.amin(Q)+np.mean(np.diff(Q))*NumPoints, np.mean(np.diff(Q)))
    r = MainFunctions.calc_r(Q)
    F_r3 = fftpack.fft(Qi_Q)
    F_r3 = F_r3[np.where(r>=0.0)]
    F_r3 = -np.imag(F_r3)*meanDeltaQ*2/np.pi
    r = np.arange(0.0, 0.0+DelR*len(F_r3), DelR)
    
    # Utility.plot_data(r, F_r3, "F_r", "r", "F(r)", "F(r) fft", "y")
    
    # ------------------------------Qi(Q) with IFFT----------------------------
    
    GR = np.zeros(len(F_r3))
    Rnn = variables.rmin
    GR[r<Rnn] = F_r3[r<Rnn]-(-4*np.pi*r[r<Rnn]*density)
    
    
    NumPoints = 2**math.ceil(math.log(len(GR)-1)/math.log(2))
    GR = Utility.resize_zero(GR, NumPoints)
    Q1 = np.linspace(0.0, 109, 550)
    DelQ = 2*np.pi/(np.mean(np.diff(r))*NumPoints)
    meanDeltar = np.mean(np.diff(r))
    Q = fftpack.fftfreq(r.size, meanDeltar)
    QiQ = fftpack.fft(GR)
    QiQ = QiQ[np.where(Q>=0.0)]
    QiQ = -np.imag(QiQ)*meanDeltar
    Q = np.arange(0.0, 0.0+DelQ*len(QiQ), DelQ)
    idxArray = np.zeros(550, dtype=np.int)
    for i in range(len(Q1)):
        idxArray[i], _ = UtilityAnalysis.find_nearest(Q, Q1[i])
    QiQ = QiQ[idxArray]
    
    Utility.plot_data(Q1, QiQ, "QiQ", "Q", "Qi(Q)", "Qi(Q) ifft", "y")
    
    # QiQ = QiQ[np.where((Q>=0.0) & (Q<=variables.maxQ))]
    # print(len(QiQ))
    # Q = np.arange(0.0, 0.0+DelQ*len(QiQ), DelQ)
    
    # Utility.plot_data(Q, QiQ, "F_r", "r", "F(r)", "F(r) fft", "y")
    
    # 
    # # Q = np.arange(0.0, 0.0+DelQ*len(QiQ), DelQ)
    # Q = np.linspace(0.0, maxQ, newDim, endpoint=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # ----------------------------F(r) optimization----------------------------
    # Qi_Q1 = np.zeros(len(SsmoothDamp_Q))
    # Qi_Q1[Q<=variables.QmaxIntegrate] = Qi_Q[Q<=variables.QmaxIntegrate]
    
    # Rnn = variables.rmin
    # F_r1 = F_r
    # DelG = np.zeros(len(F_r1))
    # DelG[r<Rnn] = F_r1[r<Rnn]-4*np.pi*r[r<Rnn]*density
    
    
    # plt.ion()
    # plt.figure("F_rIt")
    # plt.plot(r, F_r1, label="F(r)")
    # plt.xlabel("r (nm)")
    # plt.ylabel("F(r)")
    # plt.legend()
    # plt.grid(True)
    # QLimit ,_ = UtilityAnalysis.find_nearest(Q, variables.QmaxIntegrate)
    
    # for i in range(variables.iterations):
    #     Q, QiQcorr = UtilityAnalysis.calc_IFFT_Fr(r, DelG, variables.maxQ,
    #         variables.NumPoints)
        
    #     Qi_Q1[1:QLimit-1] = Qi_Q1[1:QLimit-1] - (Qi_Q1[1:QLimit-1] / 
    #         (Q[1:QLimit-1]*(Sinf + J_Q[1:QLimit-1])) + 1 ) * QiQcorr[1:QLimit-1]
        
    #     r, F_r1 = UtilityAnalysis.calc_FFT_QiQ(Q, Qi_Q1, variables.QmaxIntegrate)
    #     DelG = np.zeros(len(F_r1))
    #     DelG[r<Rnn] = F_r1[r<Rnn]-4*np.pi*r[r<Rnn]*density 
    #     Rnn = 0.99*r[np.argmin(F_r1[r<0.95*Rnn])]
        
    #     # j = i+1
    #     # plt.figure("F_rIt")
    #     # plt.plot(r, F_r1, label="%s iteration F(r)" %j)
    #     # plt.legend()
    #     # plt.draw()

    #     # time.sleep(1.0)
        
    # # plt.ioff() 
    # # Utility.plot_data(r, F_r1, "F_r", "r", "F(r)", "F(r)", "y")
    
    # SQcorr = Qi_Q1/Q + Sinf
    # QiQ = Q*(SsmoothDamp_Q-Sinf)/dampingFunction
    
    
    # Fintra_r = np.zeros(len(r))
    # print(len(Q))
    # print(len(i_Q))
    # print(len(J_Q))
    
    # F_r2, _ = Optimization.calc_optimize_Fr(variables.iterations, 
        # F_r, Fintra_r, density, i_Q, Q, Sinf, J_Q[:550], r, variables.rmin, "n")
    
    # Utility.plot_data(r, F_r2, "F_r", "r", "F(r)", "F(r)", "y")
    # Utility.plot_data(Q, QiQ, "test", "Q", "Qi(Q)", "F2(r)", "y")
    
    plt.show()
    