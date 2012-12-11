import matplotlib.pyplot as plt
import numpy as np
from block_dp import StrategicBlockCascadeSolver

def makePlot(values, ext, name, xaxis='', yaxis=''):
    ny, nx = values.shape
    xoff = float(ext[1] - ext[0])/(nx - 1)/2
    yoff = float(ext[3] - ext[2])/(ny - 1)/2
    ext = (ext[0]-xoff, ext[1]+xoff, ext[2]-yoff, ext[3]+yoff)

    f = plt.figure()
    ax = f.gca()
    p = ax.imshow(values, extent=ext, aspect='auto', origin='lower',
                  interpolation='nearest')
    cb = f.colorbar(p)
    ax.grid()
    ax.set_xlabel(xaxis, fontsize=18)
    ax.set_ylabel(yaxis, fontsize=18)
    f.savefig(name + '.pdf')
    print 'Created ' + name + '.pdf'

# CHANGE
def getStrat(p, pi, n, r):
    m = n-3
    a = int(round(m*r))
    b = m-a
    return StrategicBlockCascadeSolver(p, pi, (1,a,1,b,1),
        ((0,1,0,0,0),(1,0,1,0,0),(0,1,0,1,0),(0,0,1,0,1),(0,0,0,1,0))
        ).expectedYs()

# CHANGE
def getMyop(p, pi, n, r):
    m = n-3
    a = int(round(m*r))
    b = m-a
    return StrategicBlockCascadeSolver(p, pi, (1,a,1,b,1),
        ((0,1,0,0,0),(1,0,1,0,0),(0,1,0,1,0),(0,0,1,0,1),(0,0,0,1,0)),
        True).expectedYs()

getStratV = np.vectorize(getStrat)
getMyopV  = np.vectorize(getMyop)

pr  = (0.01, 0.5)
pir = (0.01, 2)
p = np.linspace(pr[0],   pr[1],  20)
pi = np.linspace(pir[0], pir[1], 20)
P, PI = np.meshgrid(p, pi)

ratio = np.log(getStratV(P,PI,10,0.5) / getMyopV(P,PI,10,0.5))
makePlot(ratio, pr + pir, 'cloud_n10_r0.5', 'p', 'pi')
