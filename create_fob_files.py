#!/usr/bin/env python3

"""Automate creation of files for FOB calculations in FHI-aims."""

import os
import shutil


def read_ground_inp():
    """Find number of atoms in geometry."""
    target_atom = str(input('Enter atom: '))
    with open('geometry.in', 'r') as geom_in:
        atom_counter = 0

        for line in geom_in:
            element = line.split()[-1]  # Identify atom
            identifier = line.split()[0]  # Extra check that line is an atom

            if identifier == 'atom' and element == target_atom:
                atom_counter += 1

    return target_atom, atom_counter


def create_new_controls(target_atom, num_atom):
    """Write new directories and control files to calculate FOB."""
    ks_method = 'KS_method               serial\n'
    charge = 'charge                  1.0\n'
    cube = 'output                  cube spin_density\n'

    for i in range(num_atom):
        i += 1
        os.mkdir(f'../{target_atom}{i}/')
        shutil.copyfile('control.in', f'../{target_atom}{i}/control.in')
        shutil.copyfile('geometry.in', f'../{target_atom}{i}/geometry.in')

        control = f'../{target_atom}{i}/control.in'
        fob = f'force_occupation_basis  {i} 1 atomic 1 0 0 0.0 {num_atom}\n'

        # Find and replace stuff to be changed
        with open(control, 'r') as read_control:
            content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(content):
                spl = line.split()

                # Some error checking
                if len(spl) > 1:

                    if 'force_occupation_basis' == spl[0]:
                        print('force_occupation_basis keyword already found in control.in')
                        exit(1)
                    if 'charge' == spl[0]:
                        print('charge keyword already found in control.in')
                        exit(1)
                    if 'output' == spl[0] and \
                       'cube' == spl[1] and \
                       'spin_density' == spl[2]:
                        print('spin_density cube output already specified in control.in')

                    # Change keyword lines
                    if 'KS_method' in spl:
                        content[j] = ks_method
                    if '#force_occupation_basis' in spl:
                        content[j] = fob
                    if '#' == spl[0] and 'force_occupation_basis' == spl[1]:
                        content[j] = fob
                    if '#charge' in spl:
                        content[j] = charge
                    if '#' == spl[0] and 'charge' == spl[1]:
                        content[j] = charge
                    if line.strip() == '#output                  cube spin_density':
                        content[j] = cube
                    if '#' == spl[0] and 'output' == spl[1]:
                        content[j] = cube

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
    target_atom, num_atom = read_ground_inp()
    create_new_controls(target_atom, num_atom)
