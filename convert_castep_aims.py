#!/usr/bin/env python3

import glob
import os
from ase.io import read, write


castep_inp = glob.glob('./*.cell')

geom = read(castep_inp[0])

if os.path.exists('./geometry.in'):
    print('\ngeometry.in file already exists in current directory')
    exit(1)
else:
    write('geometry.in', images=geom)
    print('\naims geometry file was written successfully')
