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

def getStrat(p, pi, n):
    return StrategicBlockCascadeSolver(p, pi, (n,), ((1,),)).expectedYs()

def getMyop(p, pi, n):
    return StrategicBlockCascadeSolver(p, pi, (n,), ((1,),), True).expectedYs()

getStratV = np.vectorize(getStrat)
getMyopV  = np.vectorize(getMyop)

pr  = (0.01, 0.5)
pir = (0.01, 10)
p = np.linspace(pr[0],   pr[1],  40)
pi = np.linspace(pir[0], pir[1], 40)
P, PI = np.meshgrid(p, pi)

ratio = getStratV(P,PI,10) / getMyopV(P,PI,10)
makePlot(ratio, pr + pir, 'clique_n10', 'p', 'pi')

pir = (0.01, 5)
nr  = (1,15)
n  = np.linspace(nr[0],   nr[1],  15)
pi = np.linspace(pir[0], pir[1], 40)
N, PI = np.meshgrid(n, pi)

ratio = getStratV(0.25,PI,N) / getMyopV(0.25,PI,N)
makePlot(ratio, nr + pir, 'clique_p0.25', 'n', 'pi')

pr = (0.01, 0.5)
nr  = (1,15)
n  = np.linspace(nr[0],   nr[1],  15)
p = np.linspace(pr[0], pr[1], 20)
N, P = np.meshgrid(n, p)

ratio = getStratV(P,1.5,N) / getMyopV(P,1.5,N)
makePlot(ratio, nr + pr, 'clique_pi1.5', 'n', 'p')
