#!/usr/bin/env python3

"""Automate creation of files for FOP calculations in FHI-aims."""

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


def create_init_files(target_atom, num_atom):
    """Write new directories and control files to calculate FOP."""
    iter_limit = 'sc_iter_limit           1\n'
    init_iter = '# sc_init_iter          75\n'
    ks_method = 'KS_method               serial\n'
    restart_file = 'restart                 restart_file\n'
    restart_save = '# restart_save_iterations 100\n'
    restart_force = '# force_single_restartfile .true.\n'
    charge = 'charge                  1.0\n'
    output_mull = '# output                 mulliken'
    output_hirsh = '# output                 hirshfeld'

    for i in range(num_atom):
        i += 1
        os.makedirs(f'../{target_atom}{i}/init')
        shutil.copyfile('control.in', f'../{target_atom}{i}/init/control.in')
        shutil.copyfile('geometry.in', f'../{target_atom}{i}/init/geometry.in')

        control = f'../{target_atom}{i}/init/control.in'

        # Find and replace stuff to be changed
        with open(control, 'r') as read_control:
            content = read_control.readlines()

            # Replace specific lines
            for i, line in enumerate(content):
                # Some error checking
                spl = line.split()
                if len(spl) > 1:
                    if 'restart' == spl[0]:
                        print('restart keyword already found in init/control.in')

                    if 'charge' == spl[0]:
                        print('charge keyword already found in control.in')
                        exit(1)

                # Replace if keyword lines are commented out
                if 'sc_iter_limit' in spl:
                    content[i] = iter_limit
                if '#sc_iter_limit' in spl:
                    content[i] = init_iter
                if '#' == spl[0] and 'sc_iter_limit' == spl[1]:
                    content[i] = init_iter
                if 'KS_method' in spl:
                    content[i] = ks_method
                if 'restart_write_only' in spl:
                    content[i] = restart_file
                if 'restart_save_iterations' in spl:
                    content[i] = restart_save
                if 'force_single_restartfile' in spl:
                    content[i] = restart_force
                if '#charge' in spl:
                    content[i] = charge
                if '#' == spl[0] and 'charge' == spl[1]:
                    content[i] = charge
                if 'output' == spl[0] and 'mulliken' == spl[1]:
                    content[i] = output_mull
                if 'output' == spl[0] and 'hirshfeld' == spl[1]:
                    content[i] = output_hirsh

            # Check if parameters not found
            no_iter_limit = False
            no_init_iter = False
            no_ks = False
            no_charge = False

            if no_iter_limit not in content:
                no_iter_limit = True
            if no_init_iter not in content:
                no_init_iter = True
            if ks_method not in content:
                no_ks = True
            if charge not in content:
                no_charge = True

        # Write the data to the file
        with open(control, 'w+') as write_control:
            write_control.writelines(content)

            # Append parameters to end of file if not found
            if no_iter_limit is True:
                write_control.write(iter_limit)
            if no_init_iter is True:
                write_control.write(iter_limit)
            if no_ks is True:
                write_control.write(ks_method)
            if no_charge is True:
                write_control.write(charge)

        print('Files and directories written successfully')

def create_hole_files():
    os.makedirs(f'../{target_atom}{i}/hole')

if __name__ == '__main__':
    target_atom, num_atom = read_ground_inp()
    create_init_files(target_atom, num_atom)
