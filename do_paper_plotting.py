from numpy import *
from matplotlib.pyplot import *
from timings import *

def do_pi():
    pi = arange(.2, 2, .005)
    ratios = calc_pi_ratios_star(.45, 20, pi)
    
    f = figure()
    plot(pi, ratios, 'or')
    xlabel('pi')
    ylabel('Best expected Y adoption: strategic/myopic')
    f.savefig('pi_ratio_p0.45n20.pdf')
    show()

def do_p():
    p = arange(0.001, .5, .001)
    ratios = calc_p_ratios_star(.9, 20, p)

    f = figure()
    plot(p, ratios, 'or')
    xlabel('p')
    ylabel('Best expected Y adoption: strategic/myopic')
    f.savefig('p_ratio_pi0.9n20.pdf')
    show()

do_pi()
do_p()
