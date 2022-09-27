#!/usr/bin/env python3

"""Automate creation of files for FOB calculations in FHI-aims."""

import os
import shutil


def read_ground_inp():
    """Find number of atoms in geometry."""
    # All element symbols up to Rf
    element_symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
                       'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K',
                       'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni',
                       'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb',
                       'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
                       'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs',
                       'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd',
                       'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                       'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb',
                       'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa',
                       'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es']

    while True:
        target_atom = str(input('Enter atom: '))

        if target_atom not in element_symbols:
            print('\nNot an element! Please enter a valid element.')
        else:
            break

    print('Enter specific atom(s) to create a core hole (leave blank for all)')
    print('Enter atom numbers one at a time and press enter after each')
    print('Enter a blank to indicate the end of the list:')

    atom_specifier = []

    # Manually select atoms for core hole
    while True:
        atom_input = input()

        if atom_input == '':
            break
        else:
            try:
                atom_input = int(atom_input)
                atom_specifier.append(atom_input)
            except ValueError:
                print('\nInvalid input! Ensure input is entered as an integer.')
                print('Enter specific atom(s) to create a core hole (leave blank for all)')
                print('Enter atom numbers one at a time and press enter after each')
                print('Enter a blank to indicate the end of the list:')

    # Default to all atoms if specific atoms aren't specified
    with open('geometry.in', 'r') as geom_in:
        atom_counter = 0

        first_iter = True
        for line in geom_in:
            spl = line.split()

            if len(spl) > 0 and 'atom' == spl[0] and target_atom in line:
                atom_counter += 1
                element = spl[-1]  # Identify atom
                identifier = spl[0]  # Extra check that line is an atom

                if identifier == 'atom' and element == target_atom:

                    if first_iter == True and len(atom_specifier) == 0:
                        first_iter = False
                        atom_specifier.append(atom_counter)
                    elif first_iter == False:
                        atom_specifier.append(atom_counter)

    # atom_specifier = [1,4,8,32,69,121]
    print('Specified atoms:', atom_specifier)
    return target_atom, atom_counter, atom_specifier


def create_new_controls(target_atom, num_targets, num_atom):
    """Write new directories and control files to calculate FOB."""
    ks_method = 'KS_method               serial\n'
    charge = 'charge                  1.0\n'
    cube = 'output                  cube spin_density\n'

    if type(num_atom) == list:
        loop_iterator = num_atom
    else:
        loop_iterator = range(num_atom)

    for i in loop_iterator:
        if type(num_atom) != list:
            i += 1

        os.mkdir(f'../{target_atom}{i}/')
        shutil.copyfile('control.in', f'../{target_atom}{i}/control.in')
        shutil.copyfile('geometry.in', f'../{target_atom}{i}/geometry.in')

        control = f'../{target_atom}{i}/control.in'
        fob = f'force_occupation_basis  {i} 1 atomic 2 1 1 0.0 {num_targets}\n'

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
    target_atom, atom_counter, num_atom = read_ground_inp()
    create_new_controls(target_atom, atom_counter, num_atom)
