#!/usr/bin/env python3

"""Automate creation of files for FOP calculations in FHI-aims."""

import os
import shutil
import subprocess
import glob


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


def create_init_files(target_atom, num_atom, at_num, atom_valence):
    """Write new init directories and control files to calculate FOP."""
    iter_limit = 'sc_iter_limit           1\n'
    init_iter = '# sc_init_iter          75\n'
    ks_method = 'KS_method               serial\n'
    restart_file = 'restart                 restart_file\n'
    restart_save = '# restart_save_iterations 100\n'
    restart_force = '# force_single_restartfile .true.\n'
    charge = 'charge                  0.1\n'
    output_mull = '# output                 mulliken\n'
    output_hirsh = '# output                 hirshfeld\n'

    # Add extra target_atom basis set
    shutil.copyfile('control.in', 'control.in.new')
    basis_set = glob.glob(f'{os.environ["SPECIES_DEFAULTS"]}/light/*{target_atom}_default')
    bash_add_basis = f'cat {basis_set[0]}'

    new_control = open('control.in.new', 'a')
    subprocess.run(bash_add_basis.split(), check=True, stdout=new_control)

    for i in range(num_atom):
        i += 1
        os.makedirs(f'../{target_atom}{i}/init')
        shutil.copyfile('control.in.new', f'../{target_atom}{i}/init/control.in')
        shutil.copyfile('geometry.in', f'../{target_atom}{i}/init/geometry.in')
        shutil.copyfile('restart_file', f'../{target_atom}{i}/init/restart_file')

        found_target_atom = False
        control = f'../{target_atom}{i}/init/control.in'
        geometry = f'../{target_atom}{i}/init/geometry.in'

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
                    # Some error checking
                    if 'restart' == spl[0]:
                        print('restart keyword already found in control.in')
                        exit(1)

                    if 'charge' == spl[0]:
                        print('charge keyword already found in control.in')
                        exit(1)

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
                    if '#charge' in spl:
                        control_content[j] = charge
                    if '#' == spl[0] and 'charge' == spl[1]:
                        control_content[j] = charge
                    if 'output' == spl[0] and 'mulliken' == spl[1]:
                        control_content[j] = output_mull
                    if 'output' == spl[0] and 'hirshfeld' == spl[1]:
                        control_content[j] = output_hirsh

            # Check if parameters not found
            no_iter_limit = False
            no_ks = False
            no_restart = False
            no_charge = False

            if iter_limit not in control_content:
                no_iter_limit = True
            if ks_method not in control_content:
                no_ks = True
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
            if no_ks is True:
                write_control.write(ks_method)
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
                        n_index = control_content[j:].index(f'    nucleus             {at_num}\n') + j
                        nucleus = control_content[n_index]  # save for hole
                        control_content[n_index] = f'    nucleus             {at_num}.1\n'

                    # Add to valence orbital
                    if '#     ion occupancy\n' in control_content[j:]:
                        v_index = control_content[j:].index('#     ion occupancy\n') + j
                        valence = control_content[v_index - 1]  # save for hole
                        control_content[v_index - 1] = atom_valence
                        break

        with open(control, 'w+') as write_control:
            write_control.writelines(control_content)

    print('init files written successfully')

    return nucleus, valence, n_index, v_index


def create_hole_files(target_atom, num_atom, nucleus, valence, n_index, v_index):
    """Write new hole directories and control files to calculate FOP."""
    iter_limit = 'sc_iter_limit           250\n'
    init_iter = 'sc_init_iter            75\n'
    ks_method = 'KS_method               parallel\n'
    restart = 'restart_read_only       restart_file\n'
    fop = 'force_occupation_projector 1 1 0.0 1 10\n'
    charge = 'charge                  1.0\n'
    output_cube = 'output                  cube spin_density\n'
    output_mull = 'output                  mulliken\n'
    output_hirsh = 'output                  hirshfeld\n'

    for i in range(num_atom):
        i += 1
        os.makedirs(f'../{target_atom}{i}/hole')
        shutil.copyfile(f'../{target_atom}{i}/init/geometry.in',
                        f'../{target_atom}{i}/hole/geometry.in')
        shutil.copyfile(f'../{target_atom}{i}/init/control.in',
                        f'../{target_atom}{i}/hole/control.in')

        control = f'../{target_atom}{i}/hole/control.in'

        with open(control, 'r') as read_control:
            control_content = read_control.readlines()

            # Replace specific lines
            for j, line in enumerate(control_content):
                spl = line.split()

                # Set nuclear and valence orbitals back to integer values
                control_content[n_index] = nucleus
                control_content[v_index - 1] = valence

                if len(spl) > 1:
                    # Some error checking
                    if 'sc_init_iter' == spl[0]:
                        print('sc_init_iter keyword already found in init/control.in')
                        exit(1)
                    if 'restart_read_only' == spl[0]:
                        print('restart_read_only keyword already found in init/control.in')
                        exit(1)
                    if 'force_occupation_projector' == spl[0]:
                        print('force_occupation_projector keyword already found in init/control.in')
                        exit(1)
                    if 'output' == spl[0] and 'cube' == spl[1] and 'spin_density' == spl[2]:
                        print('output cube spin_density already found in init/control.in')
                        exit(1)
                    if 'output' == spl[0] and 'mulliken' == spl[1]:
                        print('output mulliken already found in init/control.in')
                        exit(1)
                    if 'output' == spl[0] and 'hirshfeld' == spl[1]:
                        print('output hirshfeld already found in init/control.in')
                        exit(1)

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
    nucleus, valence, n_index, v_index = create_init_files(target_atom, num_atom, at_num, valence_orbs)
    create_hole_files(target_atom, num_atom, nucleus, valence, n_index, v_index)
