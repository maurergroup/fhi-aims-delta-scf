#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

atom = str(input('Enter atom: '))

x_axis = np.loadtxt(f'./{atom}_xps_spectrum.txt', usecols=(0))
y_axis = np.loadtxt(f'./{atom}_xps_spectrum.txt', usecols=(1))

plt.xlabel('Energy / eV')
plt.ylabel('Intensity')

plt.plot(x_axis, y_axis)
plt.savefig(f'{atom}_spectrum.png')

print(f'Spectrum saved as {atom}_spectrum.png')
