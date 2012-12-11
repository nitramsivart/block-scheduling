import matplotlib.pyplot as plt
import time
from block_dp import StrategicBlockCascadeSolver
from numpy import arange, zeros

STAR_ADJ = ((0,1),(1,0))
GRANT_ADJ = ((0,1,0,0,0),(1,0,1,0,0),(0,1,0,1,0),(0,0,1,0,1),(0,0,0,1,0))

def calc_p_ratios_star(pi, n, prange):
    timings = []
    for p in prange:
        ratio = StrategicBlockCascadeSolver(p,pi,(1,n),STAR_ADJ).expectedYs() / \
        float(StrategicBlockCascadeSolver(p,pi,(1,n),STAR_ADJ, True).expectedYs())
        timings.append(ratio)
    #plt.plot(prange, timings, 'o')
    #plt.xlabel('p', fontsize=18)
    #plt.ylabel('ratio', fontsize=18)
    #plt.show()
    return timings

def calc_pi_ratios_star(p, n, pirange):
    timings = []
    for pi in pirange:
        ratio = StrategicBlockCascadeSolver(p,pi,(1,n),STAR_ADJ).expectedYs() / \
        float(StrategicBlockCascadeSolver(p,pi,(1,n),STAR_ADJ, True).expectedYs())
        timings.append(ratio)
    #plt.plot(pirange, timings, 'o')
    #plt.xlabel('pi', fontsize=18)
    #plt.ylabel('ratio', fontsize=18)
    #plt.show()
    return timings

def calc_timings_star(p, pi, n_start, n_end, iterations):
    total_timings = zeros(n_end-n_start)
    for i in range(iterations):
        if i%2 == 0:
            continue
        timings = zeros(n_end-n_start)
        for n in range(n_start, n_end):
            start = time.clock()
            StrategicBlockCascadeSolver(p,pi,(1,n),STAR_ADJ).expectedYs()
            end = time.clock()
            timings[n-n_start] = end-start
        total_timings += timings
    total_timings = total_timings/iterations
    plt.plot(total_timings)
    plt.xlabel('n', fontsize=18)
    plt.ylabel('time (s)', fontsize=18)
    plt.show()
    return total_timings

def getStratGrant(p, pi, n, r):
    m = n-3
    a = int(round(m*r))
    b = m-a
    return StrategicBlockCascadeSolver(p, pi, (1,a,1,b,1),
        ((0,1,0,0,0),(1,0,1,0,0),(0,1,0,1,0),(0,0,1,0,1),(0,0,0,1,0))
        ).expectedYs()

def calc_timings_grant(p, pi, r, n_start, n_end, iterations):
    total_timings = zeros(n_end-n_start)
    for i in range(iterations):
        print 'iteration: ' + str(i)
        timings = zeros(n_end-n_start)
        for n in range(n_start, n_end):
            print 'n: ' + str(n)
            start = time.clock()
            getStratGrant(p, pi, n, r)
            end = time.clock()
            timings[n-n_start] = end-start
        total_timings += timings
    total_timings = total_timings/iterations
    plt.plot(total_timings)
    plt.xlabel('n', fontsize=18)
    plt.ylabel('time (s)', fontsize=18)
    plt.show()
    return total_timings

'''
In [40]: calc_timings(.3, .8, 1, 100, 30) (star)
array([  3.59400000e-04,   8.64133333e-04,   1.62243333e-03,
         2.62516667e-03,   3.83766667e-03,   5.31953333e-03,
         7.05926667e-03,   9.06606667e-03,   1.14004000e-02,
         1.38484000e-02,   1.65900333e-02,   1.96781333e-02,
         2.28856000e-02,   2.65143667e-02,   3.05801333e-02,
         3.47803333e-02,   3.93410000e-02,   4.36256000e-02,
         4.87510333e-02,   5.37424000e-02,   5.91599667e-02,
         6.56840333e-02,   7.09380333e-02,   7.63972000e-02,
         8.26227000e-02,   9.76722333e-02,   9.77265667e-02,
         1.04961333e-01,   1.15372633e-01,   1.19513300e-01,
         1.27141333e-01,   1.33464467e-01,   1.42533633e-01,
         1.53876300e-01,   1.61337333e-01,   1.70345833e-01,
         1.78946567e-01,   1.88215633e-01,   2.02001933e-01,
         2.10066233e-01,   2.25641167e-01,   2.33247900e-01,
         2.44693100e-01,   2.59427200e-01,   2.65454533e-01,
         2.75073033e-01,   2.92348700e-01,   3.07223900e-01,
         3.18635500e-01,   3.30088600e-01,   3.38905200e-01,
         3.55134767e-01,   3.69528667e-01,   3.83681867e-01,
         4.02548200e-01,   4.08210200e-01,   4.29395600e-01,
         4.43001500e-01,   4.60538767e-01,   4.71618300e-01,
         4.90251400e-01,   5.08155300e-01,   5.23142800e-01,
         5.37096000e-01,   5.52389400e-01,   5.73200867e-01,
         5.93321433e-01,   6.07694167e-01,   6.30255500e-01,
         6.47306067e-01,   6.61151433e-01,   6.89061600e-01,
         6.99749500e-01,   7.21982433e-01,   7.45117933e-01,
         7.61893200e-01,   8.02453700e-01,   7.99474367e-01,
         8.24774533e-01,   8.50944000e-01,   8.61957967e-01,
         8.98502600e-01,   9.17218900e-01,   9.45126767e-01,
         9.69301367e-01,   9.86502967e-01,   9.98975267e-01,
         1.02052390e+00,   1.05368673e+00,   1.06247270e+00,
         1.08616140e+00,   1.11604487e+00,   1.12749137e+00,
         1.16113810e+00,   1.18694450e+00,   1.20703127e+00,
         1.23494963e+00,   1.25101413e+00,   1.28420203e+00])

Timings for cloud graph:
    calc_timings_grant(.5,.5,.5,5,30,15)
array([  3.09342667e-02,   6.99743333e-02,   1.65131000e-01,
         2.76113400e-01,   4.73241800e-01,   7.32185267e-01,
         1.11780480e+00,   1.59930040e+00,   2.29756493e+00,
         3.11246100e+00,   4.21186600e+00,   5.53097907e+00,
         7.29571387e+00,   9.08574440e+00,   1.14354583e+01,
         1.40437391e+01,   1.71464914e+01,   2.08927707e+01,
         2.52741559e+01,   3.00993381e+01,   3.60933168e+01,
         4.23742486e+01,   4.99888330e+01,   5.81930697e+01,
         6.78030758e+01])
'''
