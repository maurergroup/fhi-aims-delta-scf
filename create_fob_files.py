#!/usr/bin/env python3

import os
import shutil


def read_ground_inp():
    """Find number of C in geometry."""
    target_atom = str(input('Enter atom: '))
    with open('geometry.in', 'r') as geom_in:
        atom_counter = 0

        for line in geom_in:
            element = line.split()[-1]  # Identify atom
            identifier = line.split()[0]  # Extra check that line is an atom

            if identifier == 'atom' and element == target_atom:
                atom_counter += 1

    return atom_counter


def create_new_controls(num_atom):
    """Write new directories and control files to calculate FOB."""
    for i in range(num_atom):
        i += 1
        os.mkdir(f'../C{i}/')
        shutil.copyfile('control.in', f'../C{i}/control.in')
        shutil.copyfile('geometry.in', f'../C{i}/geometry.in')

    for i in range(num_atom):
        i += 1
        control = f'../C{i}/control.in'
        ks_method = 'KS_method               parallel\n'
        fob = f'force_occupation_basis  {i} 1 atomic 1 0 0 0.0 {num_atom}\n'
        charge = 'charge                  1.0\n'
        cube = 'output                  cube spin_density\n'

        # Find and replace stuff to be changed
        with open(control, 'r') as read_control:
            content = read_control.readlines()

            # Replace specific lines
            for i, line in enumerate(content):
                # Some error checking
                if len(line.split()) > 1:
                    if 'force_occupation_basis' == line.split()[0]:
                        print('force_occupation_basis keyword already found in control.in')
                        exit(1)

                    if 'charge' == line.split()[0]:
                        print('charge keyword already found in control.in')
                        exit(1)

                    if 'output' == line.split()[0] and \
                    'cube' == line.split()[1] and \
                    'spin_density' == line.split()[2]:
                        print('spin_density cube output already specified in control.in')

                    # Replace if keyword lines are commented out
                    if 'KS_method' in line.split():
                        content[i] = ks_method
                    if '#force_occupation_basis' in line.split():
                        content[i] = fob
                    if '#' == line.split()[0] and 'force_occupation_basis' == line.split()[1]:
                        content[i] = fob
                    if '#charge' in line.split():
                        content[i] = charge
                    if '#' == line.split()[0] and 'charge' == line.split()[1]:
                        content[i] = charge
                    if line.strip() == '#output                  cube spin_density':
                        content[i] = cube
                    if '#' == line.split()[0] and 'output' == line.split()[1]:
                        content[i] = cube

            # Check if parameters not found
            no_ks = False
            no_fob = False
            no_charge = False
            no_cube = False

            if ks_method not in content:
                no_ks = True
            if fob not in content:
                no_fob = True
            if charge not in content:
                no_charge = True
            if cube not in content:
                no_cube = True

        # Write the data to the file
        with open(control, 'w+') as write_control:
            write_control.writelines(content)

            # Append parameters to end of file if not found
            if no_ks is True:
                write_control.write(ks_method)
            if no_fob is True:
                write_control.write(fob)
            if no_charge is True:
                write_control.write(charge)
            if no_cube is True:
                write_control.write(cube)

    print('Files and directories written successfully')


if __name__ == '__main__':
    num_atom = read_ground_inp()
    create_new_controls(num_atom)
