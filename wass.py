#!/usr/bin/env python3

import scipy.stats as st

files = ['aims_az', 'aims_np', 'castep_az', 'castep_np']

for i in files:
    for j in files:

        az_list = []
        np_list = []

        with open(f'./{i}_C_xps_peaks.txt', 'r') as az_file:
            for line in az_file:
                az_list.append(line)

        with open(f'./{j}_C_xps_peaks.txt', 'r') as np_file:
            for line in np_file:
                np_list.append(line)

        wass_out = st.wasserstein_distance(az_list, np_list)
        print(i)
        print(j)
        print(wass_out)
        print()
