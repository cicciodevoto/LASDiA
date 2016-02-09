# The MIT License (MIT)

# Copyright (c) 2016 Francesco Devoto

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

"""Environment for testing the software
The nomenclature and the procedures follow the article: Eggert et al. 2002 PRB, 65, 174105
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)
import six

import sys
import os

import scipy.constants as sc
from scipy import fftpack
from scipy import signal
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
import numpy as np
import time
import math

from modules.Utility import *
from modules.LiquidStructure import *
from modules.InterpolateData import *
from modules.Optimization import *
from modules.Minimization import *

# import cmath
# from cmath import exp, pi

if __name__ == '__main__':
    N = 1 # sc.N_A
    
    # Q, I_Q = read_file("./data/cea_files/HT2_034T++.chi")
    # Qbkg, I_Qbkg = read_file("./data/cea_files/HT2_036T++.chi")
    
    Q, I_Q = read_file("./data/cea_files/WO2_007BBin.chi")
    Qbkg, I_Qbkg = read_file("./data/cea_files/WO2_013BBin.chi")
    
    # minQ = 3
    # maxQ = 109
    minQ = 8
    maxQ = 100
    QmaxIntegrate = 90
    
    # BinNum = 1
    # Num = 2048 # len(Q)
    
    min_index = np.where(Q<=minQ)
    max_index = np.where((Q>QmaxIntegrate) & (Q<=maxQ))
    validation_index = np.where(Q<=maxQ)
    integration_index = np.where(Q<=QmaxIntegrate)    
    calculation_index = np.where((Q>minQ) & (Q<=QmaxIntegrate))
    
    # rebinQ = rebinning(Q, BinNum, Num, maxQ)
    # interpI_Q = interpolation(Q, I_Q, rebinQ)
    # interpI_Q[min_index] = 0.0
    
    # print(Q[55])
    # print(Q[56])
    # print(rebinQ[55])
    # print(I_Q[55], I_Q[56], I_Q[57])
    # print(interpI_Q[55], interpI_Q[56], interpI_Q[57])
    
    # peakind = signal.find_peaks_cwt(I_Q, widths = np.arange(4,6))
    
    # plt.figure(3)
    # plt.plot(Q, I_Q)
    # plt.plot(Q, I_Qbkg)
    # plt.xlabel('Q')
    # plt.ylabel('I(Q)')
    # # plt.plot(Q[peakind], I_Q[peakind], u'o')
    # # plt.plot(rebinQ, interpI_Q)
    # plt.grid()
    # plt.show()
    
    
    # elementList = {"Ar":1}
    elementList = {"C":1,"O":2}
    # test values
    # s = np.arange(0.2, 1.0, 0.1)
    # rho0 = np.arange(24, 28, 1)
    
    # real values
    # s = np.arange(0.2, 1.0, 0.01)
    # rho0 = np.arange(24.0, 28.0, 0.1)
    
    # best values
    # s = np.array([0.81])
    # rho0 = np.array([26.1])
    s = np.array([0.57])
    rho0 = np.array([26.1])

    
    chi2 = np.zeros((rho0.size, s.size))
    
    # remember the electron unit in atomic form factor!!!
    fe_Q, Ztot = calc_eeff(elementList, Q)
    Iincoh_Q = calc_Iincoh(elementList, Q)
    J_Q = calc_JQ(Iincoh_Q, Ztot, fe_Q)
    Sinf = calc_Sinf(elementList, fe_Q, Q, Ztot)

    for i, val_rho0 in enumerate(rho0):
        for j, val_s in enumerate(s):
            Isample_Q = calc_IsampleQ(I_Q, s[j], I_Qbkg)
            
            alpha = calc_alpha(J_Q, Sinf, Q, Isample_Q, fe_Q, Ztot, rho0[i], integration_index)
            Icoh_Q = calc_Icoh(N, alpha, Isample_Q, Iincoh_Q)
            
            S_Q, S_Qs = calc_SQ(N, Icoh_Q, Ztot, fe_Q, Sinf, Q, min_index, max_index, calculation_index, QmaxIntegrate)
            
            # damp = calc_damp(Q[validation_index], QmaxIntegrate)
            # S_Qdamp = (damp * (S_Q - Sinf)) + Sinf
            
            # plt.figure(1)
            # plt.plot(Q[validation_index], S_Q)
            # plt.xlabel('Q')
            # plt.ylabel('S(Q)')
            # plt.grid()
            # plt.show()
            
            # plt.figure(2)
            # plt.plot(Q[validation_index], S_Qdamp)
            # plt.grid()
            # plt.show()

            
            # easy test!!!
            # S_Q = S_Qdamp
            
            i_Q = calc_iQ(S_Q, Sinf)
            Qi_Q = Q[validation_index] * i_Q
            plt.figure(2)
            plt.plot(Q, Qi_Q)
            plt.xlabel('Q')
            plt.ylabel('Qi(Q)')
            plt.grid()
            plt.show()
            
            DeltaQ = np.diff(Q)
            meanDeltaQ = np.mean(DeltaQ)
            r = fftpack.fftfreq(Q[validation_index].size, meanDeltaQ)
            mask = np.where(r>0)
            
            F_r = calc_Fr(r[mask], Q[integration_index], i_Q[integration_index])
            
            # plt.figure(1)
            # plt.plot(r[mask], F_r)
            # plt.xlabel('r')
            # plt.ylabel('F(r)')
            # plt.grid()
            # plt.show()
            
            iteration = 2
            rmin = 0.22
            
            Fintra_r = calc_Fintra(r[mask], Q, QmaxIntegrate)
            plt.figure(1)
            plt.plot(r[mask], Fintra_r)
            plt.xlabel('r')
            plt.ylabel('Fintra(r)')
            plt.grid()
            plt.show()
            F_rIt = calc_optimize_Fr(iteration, F_r, Fintra_r, rho0[i], i_Q[integration_index], Q[integration_index], Sinf, J_Q[integration_index], r[mask], rmin)
            plt.show()
            
            # maskIt = np.where((r>0) & (r < rmin))
            # rIt = r[maskIt]
            # Fintra_r = calc_Fintra(rIt)
            # deltaF_r = calc_deltaFr(F_rIt[maskIt], Fintra_r, rIt, rho0[i])
            # chi2[i][j] = simps(deltaF_r**2, rIt)
        
    # minIndxRho0, minIndxS = np.unravel_index(chi2.argmin(), chi2.shape)
    # print(chi2[minIndxRho0][minIndxS])
    # print(rho0[minIndxRho0], s[minIndxS])
    
    # print(chi2)
    # print(chi2[0, : ])
    # print(chi2.shape)
    
    # plt.figure(5)
    # plt.plot(s,chi2[0, : ])
    # # plt.plot(rho0,chi2[ : ,0])
    # # plt.xlabel('rho0')
    # plt.xlabel('s')
    # plt.ylabel('chi2')
    # plt.grid()
    # plt.show()
    
    # x, y = np.meshgrid(s, rho0)
    # fig = plt.figure(3)
    # ax = Axes3D(fig)
    # ax.plot_surface(x, y, chi2, rstride=1, cstride=1, cmap='rainbow')
    
    # plt.figure(4)
    # plt.contour(s, rho0, chi2, 200)
    # plt.show()
