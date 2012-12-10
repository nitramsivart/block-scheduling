import matplotlib.pyplot as plt
import time
from block_dp import StrategicBlockCascadeSolver
from numpy import arange, zeros
from pylab import *

STAR_ADJ = ((0,1),(1,0))

def p_vs_pi(p, pi):
    return StrategicBlockCascadeSolver(p, pi, (1, 10), STAR_ADJ).expectedYs() / \
           StrategicBlockCascadeSolver(p, pi, (1, 10), STAR_ADJ, True).expectedYs()


def p_vs_n(p, n):
    return StrategicBlockCascadeSolver(p, .9, (1, n), STAR_ADJ).expectedYs() / \
           StrategicBlockCascadeSolver(p, .9, (1, n), STAR_ADJ, True).expectedYs()

def pi_vs_n(pi, n):
    return StrategicBlockCascadeSolver(.45, pi, (1, n), STAR_ADJ).expectedYs() / \
           StrategicBlockCascadeSolver(.45, pi, (1, n), STAR_ADJ, True).expectedYs()


def do_plotting(xlist,ylist, Z, x_start, x_inc, y_start, y_inc, dim, xlabel, ylabel, name):
    X,Y = meshgrid(xlist, ylist)
    f = plt.figure()
    ax = f.gca()
    #ax.grid()
    plt.pcolor(X, Y, Z, vmax=abs(Z).max(), vmin=abs(Z).min())
    plt.axis([x_start, x_start + x_inc*float(dim-1), y_start,
              y_start + y_inc*float(dim-1)])
    plt.xlabel(xlabel, fontsize=18)
    plt.ylabel(ylabel, fontsize=18)
    plt.colorbar()
    f.savefig(name + '.pdf')

def x_vs_y(x_start, x_inc, y_start, y_inc, dim, func, x_label, y_label, name):
    x_list = arange(x_start, x_start + x_inc * float(dim), x_inc)
    y_list = arange(y_start, y_start + y_inc * float(dim), y_inc)
    Z = zeros((dim, dim))
    for i in range(dim):
        for j in range(dim):
            Z[j, i] = func(x_list[i], y_list[j])
    do_plotting(x_list, y_list, Z, x_start, x_inc, 
                y_start, y_inc, dim, x_label, y_label, name)
    return x_list, y_list, Z

x_vs_y(.1, .01, .2, .025, 40, p_vs_pi, 'p', 'pi', 'star_n10')
x_vs_y(.1, .01, 1, 1, 40, p_vs_n, 'p', 'n', 'star_pi0.9')
x_vs_y(.2, .025, 1, 1, 40, pi_vs_n, 'pi', 'n', 'star_p0.45')
