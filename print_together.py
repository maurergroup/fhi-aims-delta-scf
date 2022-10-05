#!/usr/bin/env python3 

import numpy as np
import matplotlib.pyplot as plt

x_axis_aims = np.loadtxt('./aims_az_C_xps_spectrum.txt', usecols=(0))
y_axis_aims = np.loadtxt('./aims_az_C_xps_spectrum.txt', usecols=(1))

aims_y_max = y_axis_aims.max()
aims_y_max_arg = y_axis_aims.argmax()
aims_be = x_axis_aims[aims_y_max_arg]
aims_be_line = [i for i in np.linspace(-0.6, aims_y_max, num=len(y_axis_aims))]

x_axis_cas = np.loadtxt('./castep_az_C_xps_spectrum.txt', usecols=(0))
y_axis_cas = np.loadtxt('./castep_az_C_xps_spectrum.txt', usecols=(1))

cas_y_max = y_axis_cas.max()
cas_y_max_arg = y_axis_cas.argmax()
cas_be = x_axis_cas[cas_y_max_arg]
cas_be_line = [i for i in np.linspace(-0.6, cas_y_max, num=len(y_axis_cas))]

plt.xlabel('Energy / eV')
plt.ylabel('Intensity')

plt.plot([i for i in np.linspace(280, 295, 5)], np.full((5), 0), color='black',
         zorder=10)
plt.plot(np.full((len(aims_be_line)), aims_be), aims_be_line, c='grey',
         linestyle='--', label='Binding Energy', zorder=5)
plt.plot(np.full((len(cas_be_line)), cas_be), cas_be_line, c='grey',
         linestyle='--', zorder=0)

plt.plot(x_axis_aims, y_axis_aims, label='FHI-aims')
plt.plot(x_axis_cas, y_axis_cas, label='CASTEP')
plt.ylim((-2, 13))
plt.legend(loc='upper center')
# plt.title('Naphthalene / Cu(111)')
spectrum='az_spectrum.png'
plt.savefig(spectrum)

print(f'Spectrum saved as {spectrum}')
