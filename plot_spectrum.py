#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

x_axis = np.loadtxt('./C_xps_spectrum.txt', usecols=(0))
y_axis = np.loadtxt('./C_xps_spectrum.txt', usecols=(1))

plt.xlabel('Energy / eV')
plt.ylabel('Intensity')

plt.plot(x_axis, y_axis)
plt.savefig('spectrum.png')
