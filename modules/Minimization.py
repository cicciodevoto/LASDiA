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

"""Set of modules used in LASDiA to calculate the chi2 minimization.

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
from scipy import fftpack
from scipy.integrate import simps
from scipy.stats import chisquare

from modules.Optimization import *


def calc_chi2(r, rmin, F_rIt, Fintra_r, rho0):
    """
    """
    
    maskIt = np.where((r>0) & (r < rmin))
    rIt = r[maskIt]
    deltaF_r = calc_deltaFr(F_rIt[maskIt], Fintra_r[maskIt], rIt, rho0)
    
    chi2 = simps(deltaF_r**2, r[maskIt])
    
    return chi2
    
    
def calc_min_chi2(s, rho0, chi2):
    """
    """
    
    # take min of chi2
    minIndxRho0, minIndxS = np.unravel_index(chi2.argmin(), chi2.shape)
    # maxIndxRho0, maxIndxS = np.unravel_index(chi2.argmax(), chi2.shape)
    # print(chi2[minIndxRho0][minIndxS])
    # print(chi2[maxIndxRho0][maxIndxS])
    # print("chi2 min ", chi2[minIndxRho0][minIndxS])
    # print("rho0 ", rho0[minIndxRho0], "s ", s[minIndxS])
    
    return (chi2[minIndxRho0][minIndxS], s[minIndxS], minIndxS, rho0[minIndxRho0], minIndxRho0)
