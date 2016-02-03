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

"""Set of modules used in LASDiA to calculate the F(r) optimization.

The nomenclature and the procedure follow the article:
Eggert et al. 2002 PRB, 65, 174105.

For the functions arguments and the returns I followed this convetion for the notes:
arguments: description - type
returns: description - type.

For the variables name I used this convention:
if the variable symbolizes a function, its argument is preceded by an underscore: f(x) -> f_x
otherwise it is just the name.
"""

import matplotlib.pyplot as plt

import sys
import os

import numpy as np
import scipy.constants as sc
import time
from scipy import fftpack
from scipy.integrate import simps

from lmfit import minimize, Parameters

from modules.LiquidStructure import *

def calc_Fintra(r):
    """Function to calculate the intramolecular contribution of F(r) (eq. 42)
    
    To implemente!!!
    """
    
    Fintra_r = np.zeros(r.size)
    
    return Fintra_r
    
    
def calc_deltaFr(F_r, Fintra_r, r, rho0):
    """Function to calculate deltaF(r) (eq. 44, 48)
    
    arguments:
    F_r: F(r) - array
    Fintra_r: intramolecular contribution of F(r) - array
    r: radius - array
    rho0: average atomic density - number
    
    return:
    deltaF_r: deltaF(r) - array
    """
    
    deltaF_r = F_r - (Fintra_r - 4*np.pi*r*rho0)
    
    return deltaF_r
    

def calc_iQi(i_Q, Q, Sinf, J_Q, deltaF_r, r, rmin):
    """Function to calculate the i-th iteration of i(Q) (eq. 46, 49)
    
    arguments:
    i_Q: i(Q) - array
    Q: momentum transfer - array
    Sinf: Sinf - number
    J_Q: J(Q) - array
    deltaF_r: deltaF(r) - array
    rmin: value of r cutoff - number
    
    returns:
    i_Qi: i-th iteration of i(Q) - array
    """
    
    mask = np.where(r < rmin)
    rInt = r[mask]
    deltaF_rInt = deltaF_r[mask]
    
    integral = simps(deltaF_rInt * (np.array(np.sin(np.mat(rInt).T *  np.mat(Q)))).T, rInt)
    i_Qi = i_Q - ( 1/Q * ( i_Q / (Sinf + J_Q) + 1)) * integral
         
    return i_Qi

    
def calc_optimize_Fr(iteration, F_r, rho0, i_Q, Q, Sinf, J_Q, r, rmin):
    """Function to calculate the F(r) optimization (eq 47, 48, 49)
    
    arguments:
    iteration: number of iteration - number
    F_r: initial value of F(r) - array
    rho0: average atomic density - number
    i_Q: i(Q) - array
    Q: momentum transfer - array
    Sinf: Sinf - number
    J_Q: J(Q) - array
    r: radius - array
    rmin: value of r cutoff - number
    
    returns:
    F_r: optimazed F(r) - array
    """
    
    # commented just for testing the damping factor!!!
    # plt.figure()
    # plt.plot(r, F_r)
    # plt.grid()
    # plt.ion()
    
    Fintra_r = calc_Fintra(r)
    for i in range(iteration):
        deltaF_r = calc_deltaFr(F_r, Fintra_r, r, rho0)
        i_Q = calc_iQi(i_Q, Q, Sinf, J_Q, deltaF_r, r, rmin)
        F_r = calc_Fr(r, Q, i_Q)
        # plt.plot(r, F_r)
        # plt.draw()
        # time.sleep(1.0)
    
    # plt.ioff()
    # plt.show()
    
    return F_r
    
    
    
    
