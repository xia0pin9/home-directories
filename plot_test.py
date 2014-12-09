__author__ = 'rain'

# import numpy as np
# import matplotlib.pyplot as plt
#
# N = 50
# x = np.random.rand(N)
# y = np.random.rand(N)
#
# plt.scatter(x, y)
# print(plt.plot(range(20), range(20)))
# plt.show()

# import pylab
# x = pylab.arange(0, 10, 0.1)
# y = pylab.sin(x)
# pylab.plot(x,y, 'ro-')
# pylab.ion()
# pylab.show()

import matplotlib
print(matplotlib.get_backend())
matplotlib.use("TKAgg")
from matplotlib.pyplot import plot, draw, show
plot([1, 2, 3])
# draw()
print 'continue computation'
import matplotlib.rcsetup as rc
print(rc.all_backends)
# at the end call show to ensure window won't close.
show()
