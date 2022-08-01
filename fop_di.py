#!/usr/bin/env python3
"""Automate creation of files for FOP calculations in FHI-aims."""

import os
import shutil
import subprocess
import glob
import numpy as np


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

    # Manually select atoms for core hole
    atom_specifier = []

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
    if len(atom_specifier) == 0:
        with open('geometry.in', 'r') as geom_in:
            atom_counter = 0

            for line in geom_in:
                spl = line.split()

                if len(spl) > 0 and 'atom' == spl[0]:
                    atom_counter += 1
                    element = spl[-1]  # Identify atom
                    identifier = spl[0]  # Extra check that line is an atom

                    if identifier == 'atom' and element == target_atom:
                        atom_specifier.append(atom_counter)

        print('Specified atoms:', atom_specifier)

        return target_atom, atom_counter

    else:
        print('Specified atoms:', atom_specifier)
        return target_atom, atom_specifier


def get_electronic_structure(target_atom):
    """Get valence electronic structure of target atom"""
    # Adapted from scipython.com question P2.5.12

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

    atom_index = element_symbols.index(str(target_atom)) + 1

    # Letters identifying subshells
    l_letter = ['s', 'p', 'd', 'f', 'g']

    def get_config_str(config):
        """Turn a list of orbital, nelec pairs into a configuration string."""
        return '.'.join(['{:2s}{:d}'.format(*e) for e in config])

    # Create and order a list of tuples, (n+l, n, l), corresponding to the order
    # in which the corresponding orbitals are filled using the Madelung rule.
    nl_pairs = []
    for n in range(1,8):
        for l in range(n):
            nl_pairs.append((n+l, n, l))
    nl_pairs.sort()

    # inl indexes the subshell in the nl_pairs list; nelec is the number of
    # electrons currently inhabiting this subshell
    inl, nelec = 0, 0
    # start with the 1s orbital
    n, l = 1, 0
    # a list of orbitals and the electrons they contain for a configuration
    config = [['1s', 0]]
    # Store the most recent Noble gas configuration encountered in a tuple with the
    # corresponding element symbol
    noble_gas_config = ('', '')

    for i, _ in enumerate(element_symbols[:atom_index]):
        nelec += 1

        if nelec > 2*(2*l+1):
            # this subshell is now full
            if l == 1:
                # The most recent configuration was for a Noble gas: store it
                noble_gas_config = (get_config_str(config),
                                    '[{}]'.format(element_symbols[i-1]))
            # Start a new subshell
            inl += 1
            _, n, l = nl_pairs[inl]
            config.append(['{}{}'.format(n, l_letter[l]), 1])
            nelec = 1
        else:
            # add an electron to the current subshell
            config[-1][1] += 1

        # Turn config into a string
        s_config = get_config_str(config)
        # Replace the heaviest Noble gas configuration with its symbol
        s_config = s_config.replace(*noble_gas_config)
        # print('{:2s}: {}'.format(element, s_config))

    output = list(s_config.split('.').pop(-1))
    valence = f'    valence      {output[0]}  {output[1]}   {output[2]}.1\n'

    return atom_index, valence


def create_init_1_files(target_atom, num_atom, at_num, atom_valence):
    """Write new init directories and control files to calculate FOP."""
    iter_limit = '# sc_iter_limit           1\n'
    init_iter = '# sc_init_iter          75\n'
    ks_method = 'KS_method                 serial\n'
    restart_file = 'restart_write_only        restart_file\n'
    restart_save = 'restart_save_iterations   20\n'
    restart_force = '# force_single_restartfile  .true.\n'
    charge = 'charge                    0.1\n'
    output_cube = 'output                  cube spin_density\n'
    output_mull = '# output                  mulliken\n'
    output_hirsh = '# output                  hirshfeld\n'

    # Add extra target_atom basis set
    while True:
        basis_set_opts = ['light', 'intermediate', 'tight', 'really_tight']
        basis_set = str(input('Enter the species default basis set level: '))

        if basis_set not in basis_set_opts:
            print('Not a valid basis set option! The following basis set options are valid:')
            print(*basis_set_opts, sep='    ')
        else:
            break

    shutil.copyfile('control.in', 'control.in.new')
    basis_set = glob.glob(f'{os.environ["SPECIES_DEFAULTS"]}/defaults_2020/{basis_set}/*{target_atom}_default')
    bash_add_basis = f'cat {basis_set[0]}'

    new_control = open('control.in.new', 'a')
    subprocess.run(bash_add_basis.split(), check=True, stdout=new_control)

    if type(num_atom) == list:
        loop_iterator = num_atom
    else:
        loop_iterator = range(num_atom)

    for i in loop_iterator:
        if type(num_atom) != list:
            i += 1

        os.makedirs(f'../{target_atom}{i}/init_1')
        shutil.copyfile('control.in.new', f'../{target_atom}{i}/init_1/control.in')
        shutil.copyfile('geometry.in', f'../{target_atom}{i}/init_1/geometry.in')

        found_target_atom = False
        control = f'../{target_atom}{i}/init_1/control.in'
        geometry = f'../{target_atom}{i}/init_1/geometry.in'

        # Change geometry file
        with open(geometry, 'r') as read_geom:
            geom_content = read_geom.readlines()

            # Change atom to {atom}{num}
            atom_counter = 0
            for j, line in enumerate(geom_content):
                spl = line.split()

                if 'atom' in line and target_atom in line:
                    if atom_counter + 1 == i:
                        partial_hole_atom = f' {target_atom}1\n'
                        geom_content[j] = ' '.join(spl[0:-1]) + partial_hole_atom

                    atom_counter += 1

        with open(geometry, 'w+') as write_geom:
            write_geom.writelines(geom_content)

        # Change control file
        with open(control, 'r') as read_control:
            control_content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(control_content):
                spl = line.split()

                if len(spl) > 1:
                    # Fix basis sets
                    if 'species' == spl[0] and target_atom == spl[1]:
                        if found_target_atom is False:
                            control_content[j] = f'  species        {target_atom}1\n'
                            found_target_atom = True

                    # Change keyword lines
                    if 'sc_iter_limit' in spl:
                        control_content[j] = iter_limit
                    if 'sc_init_iter' in spl:
                        control_content[j] = init_iter
                    if 'KS_method' in spl:
                        control_content[j] = ks_method
                    if 'restart_write_only' in spl:
                        control_content[j] = restart_file
                    if 'restart_save_iterations' in spl:
                        control_content[j] = restart_save
                    if 'force_single_restartfile' in spl:
                        control_content[j] = restart_force
                    if 'charge' in spl:
                        control_content[j] = charge
                    if '#' == spl[0] and 'charge' == spl[1]:
                        control_content[j] = charge
                    if 'cube spin_density' in spl:
                        control_content[j] = output_cube
                    if 'output' == spl[0] and 'mulliken' == spl[1]:
                        control_content[j] = output_mull
                    if 'output' == spl[0] and 'hirshfeld' == spl[1]:
                        control_content[j] = output_hirsh

            # Check if parameters not found
            no_iter_limit = False
            no_ks = False
            no_restart = False
            no_charge = False
            no_cube = False

            if iter_limit not in control_content:
                no_iter_limit = True
            if ks_method not in control_content:
                no_ks = True
            if restart_file not in control_content:
                no_restart = True
            if charge not in control_content:
                no_charge = True
            if output_cube not in control_content:
                no_cube = True

        # Write the data to the file
        with open(control, 'w+') as write_control:
            write_control.writelines(control_content)

            # Append parameters to end of file if not found
            if no_iter_limit is True:
                write_control.write(iter_limit)
            if no_ks is True:
                write_control.write(ks_method)
            if no_restart is True:
                write_control.write(restart_file)
            if no_charge is True:
                write_control.write(charge)
            if no_cube is True:
                write_control.write(output_cube)

        # Add 0.1 charge
        with open(control, 'r') as read_control:
            control_content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(control_content):
                spl = line.split()

                if target_atom + '1' in spl:
                    # Add to nucleus
                    if f'    nucleus             {at_num}\n' in control_content[j:]:
                        n_index = control_content[j:].index(f'    nucleus             {at_num}\n') + j
                        nucleus = control_content[n_index]  # save for hole
                        control_content[n_index] = f'    nucleus             {at_num}.1\n'
                    elif f'    nucleus      {at_num}\n' in control_content[j:]:
                        n_index = control_content[j:].index(f'    nucleus      {at_num}\n') + j
                        nucleus = control_content[n_index]  # save for hole
                        control_content[n_index] = f'    nucleus      {at_num}.1\n'

                    # Add to valence orbital
                    if '#     ion occupancy\n' in control_content[j:]:
                        vbs_index = control_content[j:].index('#     valence basis states\n') + j
                        io_index = control_content[j:].index('#     ion occupancy\n') + j

                        # Check which orbital to add 0.1 to
                        principle_qns = np.array([])
                        azimuthal_orbs = np.array([])
                        azimuthal_qns = np.zeros(io_index - vbs_index - 1)
                        azimuthal_refs = {
                            's': 1,
                            'p': 2,
                            'd': 3,
                            'f': 4
                        }

                        # Get azimuthal and principle quantum numbers
                        for count, valence_orbital in enumerate(control_content[vbs_index+1:io_index]):
                            principle_qns = np.append(principle_qns, np.array(valence_orbital.split()[1])).astype(int)
                            azimuthal_orbs = np.append(azimuthal_orbs, np.array(valence_orbital.split()[2]))
                            azimuthal_qns[count] = azimuthal_refs[azimuthal_orbs[count]]
                            azimuthal_qns = azimuthal_qns.astype(int)

                        # Find the orbital with highest principle and azimuthal qn
                        highest_n = np.amax(principle_qns)
                        highest_n_index = np.where(principle_qns == highest_n)

                        # Check for highest l if 2 orbitals have the same n
                        if len(highest_n_index[0]) > 1:
                            highest_l = np.amax(azimuthal_qns)
                            highest_l_index = np.where(azimuthal_qns == highest_l)
                            addition_state = np.intersect1d(highest_n_index, highest_l_index)[0]
                        else:
                            addition_state = highest_n_index[0][0]

                        # Add the 0.1 electron
                        valence = control_content[vbs_index + addition_state + 1]  # save for write hole file
                        valence_index = vbs_index + addition_state + 1
                        control_content[valence_index] = atom_valence
                        break

        with open(control, 'w+') as write_control:
            write_control.writelines(control_content)

    print('init_1 files written successfully')

    return nucleus, valence, n_index, valence_index


def create_init_2_files(target_atom, num_atom, at_num, atom_valence, n_index, valence_index):
    """Write new init directories and control files to calculate FOP."""
    ks_states = [0, 0]
    print()
    print('Enter KS start and KS stop states (press enter after each)')

    while True:
        try:
            ks_states[0] = int(input('KS start: '))
            ks_states[1] = int(input('KS stop: '))
            break
        except ValueError:
            print('\nInvalid input! Ensure input is entered as an integer.')
            print('Enter KS start and KS stop states (press enter after each)')

    iter_limit = 'sc_iter_limit             1\n'
    restart_file = 'restart             restart_file\n'
    restart_force = '# force_single_restartfile .true.\n'
    charge = 'charge                    1.1\n'
    fop = f'force_occupation_projector {ks_states[0]} 1 0.0 {ks_states[0]} {ks_states[1]}\n'

    if type(num_atom) == list:
        loop_iterator = num_atom
    else:
        loop_iterator = range(num_atom)

    for i in loop_iterator:
        if type(num_atom) != list:
            i += 1

        os.makedirs(f'../{target_atom}{i}/init_2')
        shutil.copyfile('control.in.new', f'../{target_atom}{i}/init_2/control.in')
        shutil.copyfile(f'../{target_atom}{i}/init_1/geometry.in', f'../{target_atom}{i}/init_2/geometry.in')

        found_target_atom = False
        control = f'../{target_atom}{i}/init_2/control.in'

        # Change control file
        with open(control, 'r') as read_control:
            control_content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(control_content):
                spl = line.split()

                if len(spl) > 1:
                    # Fix basis sets
                    if 'species' == spl[0] and target_atom == spl[1]:
                        if found_target_atom is False:
                            control_content[j] = f'  species        {target_atom}1\n'
                            found_target_atom = True

                    # Change keyword lines
                    if 'sc_iter_limit' in spl:
                        control_content[j] = iter_limit
                    if 'restart_write_only' in spl:
                        control_content[j] = restart_file
                    if 'force_single_restartfile' in spl:
                        control_content[j] = restart_force
                    if '#force_occupation_projector' == spl[0]:
                        control_content[j] = fop
                    if 'charge' in spl:
                        control_content[j] = charge
                    if '#' == spl[0] and 'charge' == spl[1]:
                        control_content[j] = charge

            # Check if parameters not found
            no_iter_limit = False
            no_restart = False
            no_charge = False

            if iter_limit not in control_content:
                no_iter_limit = True
            if restart_file not in control_content:
                no_restart = True
            if charge not in control_content:
                no_charge = True

        # Write the data to the file
        with open(control, 'w+') as write_control:
            write_control.writelines(control_content)

            # Append parameters to end of file if not found
            if no_iter_limit is True:
                write_control.write(iter_limit)
            if no_restart is True:
                write_control.write(restart_file)
            if no_charge is True:
                write_control.write(charge)

        # Add 0.1 charge
        with open(control, 'r') as read_control:
            control_content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(control_content):
                spl = line.split()

                if target_atom + '1' in spl:
                    # Add to nucleus
                    if f'    nucleus             {at_num}\n' in control_content[j:]:
                        nucleus = control_content[n_index]  # save for hole
                        control_content[n_index] = f'    nucleus             {at_num}.1\n'
                    elif f'    nucleus      {at_num}\n' in control_content[j:]:
                        nucleus = control_content[n_index]  # save for hole
                        control_content[n_index] = f'    nucleus      {at_num}.1\n'

                    # Add to valence orbital
                    if '#     ion occupancy\n' in control_content[j:]:

                        # Add the 0.1 electron
                        control_content[valence_index] = atom_valence
                        break

        with open(control, 'w+') as write_control:
            write_control.writelines(control_content)

    print('init_2 files written successfully')

    return ks_states


def create_hole_files(ks_states, target_atom, num_atom, nucleus, valence, n_index, valence_index):
    """Write new hole directories and control files to calculate FOP."""
    iter_limit = 'sc_iter_limit             1000\n'
    init_iter = 'sc_init_iter              75\n'
    ks_method = 'KS_method                serial\n'
    restart = 'restart_read_only       restart_file\n'
    charge = 'charge                    1.0\n'
    fop = f'force_occupation_projector {ks_states[0]} 1 0.0 {ks_states[0]} {ks_states[1]}\n'
    output_cube = 'output                  cube spin_density\n'
    output_mull = 'output                  mulliken\n'
    output_hirsh = 'output                  hirshfeld\n'

    if type(num_atom) == list:
        loop_iterator = num_atom
    else:
        loop_iterator = range(num_atom)

    for i in loop_iterator:
        if type(num_atom) != list:
            i += 1

        os.makedirs(f'../{target_atom}{i}/hole')
        shutil.copyfile(f'../{target_atom}{i}/init_1/geometry.in',
                        f'../{target_atom}{i}/hole/geometry.in')
        shutil.copyfile(f'../{target_atom}{i}/init_1/control.in',
                        f'../{target_atom}{i}/hole/control.in')

        control = f'../{target_atom}{i}/hole/control.in'

        with open(control, 'r') as read_control:
            control_content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(control_content):
                spl = line.split()

                # Set nuclear and valence orbitals back to integer values
                control_content[n_index] = nucleus
                control_content[valence_index] = valence

                if len(spl) > 1:

                    # Change keyword lines
                    if 'sc_iter_limit' in spl:
                        control_content[j] = iter_limit
                    if '#sc_init_iter' in spl:
                        control_content[j] = init_iter
                    if '#' == spl[0] and 'sc_init_iter' == spl[1]:
                        control_content[j] = init_iter
                    if 'KS_method' in spl:
                        control_content[j] = ks_method
                    if 'restart' == spl[0]:
                        control_content[j] = restart
                    if '#force_occupation_projector' == spl[0]:
                        control_content[j] = fop
                    if '#' == spl[0] and 'force_occupation_projector' == spl[1]:
                        control_content[j] = fop
                    if 'charge' in spl:
                        control_content[j] = charge
                    if ['#output', 'cube', 'spin_density'] == spl or ['#', 'output', 'cube', 'spin_density'] == spl:
                        control_content[j] = output_cube
                    if ['#output', 'hirshfeld'] == spl or ['#', 'output', 'hirshfeld'] == spl:
                        control_content[j] = output_hirsh
                    if ['#output', 'mulliken'] == spl or ['#', 'output', 'mulliken'] == spl:
                        control_content[j] = output_mull

            # Check if parameters not found
            no_init_iter = False
            no_restart = False
            no_fop = False
            no_output_cube = False
            no_output_mull = False
            no_output_hirsh = False

            if init_iter not in control_content:
                no_init_iter = True
            if restart not in control_content:
                no_restart = True
            if fop not in control_content:
                no_fop = True
            if output_cube not in control_content:
                no_output_cube = True
            if output_mull not in control_content:
                no_output_mull = True
            if output_hirsh not in control_content:
                no_output_hirsh = True

        # Write the data to the file
        with open(control, 'w+') as write_control:
            write_control.writelines(control_content)

            # Append parameters to end of file if not found
            if no_init_iter is True:
                write_control.write(init_iter)
            if no_restart is True:
                write_control.write(restart)
            if no_fop is True:
                write_control.write(fop)
            if no_output_cube is True:
                write_control.write(output_cube)
            if no_output_mull is True:
                write_control.write(output_mull)
            if no_output_hirsh is True:
                write_control.write(output_hirsh)

    print('hole files written successfully')


if __name__ == '__main__':
    target_atom, num_atom = read_ground_inp()
    at_num, valence_orbs = get_electronic_structure(target_atom)
    nucleus, valence, n_index, valence_index = create_init_1_files(target_atom, num_atom, at_num, valence_orbs)
    ks_states = create_init_2_files(target_atom, num_atom, at_num, valence_orbs, n_index, valence_index)
    create_hole_files(ks_states, target_atom, num_atom, nucleus, valence, n_index, valence_index)
