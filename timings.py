import matplotlib.pyplot as plt
import time
from block_dp import StrategicBlockCascadeSolver
from numpy import zeros

def calc_timings(p, pi, n_start, n_end, iterations):
    total_timings = zeros(n_end-n_start)
    for i in range(iterations):
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
