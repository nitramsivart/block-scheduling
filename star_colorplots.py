import matplotlib.pyplot as plt
from block_dp import StrategicBlockCascadeSolver
from numpy import arange, zeros
from pylab import *

def p_vs_pi(p, pi):
    return StrategicBlockCascadeSolver(p, pi, (1, 10), ((0,1),(1,0))).expectedYs() / \
           StrategicBlockCascadeSolver(p, pi, (1, 10), ((0,1),(1,0)), True).expectedYs()


def p_vs_n(p, n):
    return StrategicBlockCascadeSolver(p, .9, (1, n), ((0,1),(1,0))).expectedYs() / \
           StrategicBlockCascadeSolver(p, .9, (1, n), ((0,1),(1,0)), True).expectedYs()

def pi_vs_n(pi, n):
    return StrategicBlockCascadeSolver(.45, pi, (1, n), ((0,1),(1,0))).expectedYs() / \
           StrategicBlockCascadeSolver(.45, pi, (1, n), ((0,1),(1,0)), True).expectedYs()


def do_plotting(xlist,ylist, Z, x_start, x_inc, y_start, y_inc, dim, xlabel, ylabel):
    X,Y = meshgrid(xlist, ylist)
    plt.pcolor(X, Y, Z, vmax=abs(Z).max(), vmin=0)
    plt.axis([x_start, x_start + x_inc*float(dim-1), y_start, y_start + y_inc*float(dim-1)])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.colorbar()
    plt.show()

def x_vs_y(x_start, x_inc, y_start, y_inc, dim, func, x_label, y_label):
    x_list = arange(x_start, x_start + x_inc * float(dim), x_inc)
    y_list = arange(y_start, y_start + y_inc * float(dim), y_inc)
    Z = zeros((dim, dim))
    for i in range(dim):
        for j in range(dim):
            Z[j, i] = func(x_list[i], y_list[j])
    do_plotting(x_list, y_list, Z, x_start, x_inc, y_start, y_inc, dim, x_label, y_label)

x_vs_y(.1, .01, .2, .025, 40, p_vs_pi, 'p', 'pi')
x_vs_y(.1, .01, 1, 1, 40, p_vs_n, 'p', 'n')
x_vs_y(.2, .025, 1, 1, 40, pi_vs_n, 'pi', 'n')
