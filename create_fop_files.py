#!/usr/bin/env python3

"""Automate creation of files for FOP calculations in FHI-aims."""

import os
import shutil
import subprocess


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

    found_target_atom = False

    # Add extra target_atom basis set
    bash_cmd = f'cat $SPECIES_DEFAULTS/light/*{target_atom}* >> control.in'
    subprocess.run(bash_cmd.split())

    for i in range(num_atom):
        i += 1
        os.makedirs(f'../{target_atom}{i}/init')
        shutil.copyfile('control.in', f'../{target_atom}{i}/init/control.in')
        shutil.copyfile('geometry.in', f'../{target_atom}{i}/init/geometry.in')
        shutil.copyfile('restart_file', f'../{target_atom}{i}/init/restart_file')

        control = f'../{target_atom}{i}/init/control.in'
        geometry = f'../{target_atom}{i}/init/geometry.in'

        # Change geometry file
        with open(geometry, 'r') as read_geom:
            geom_content = read_geom.readlines()

            # Change atom to {atom}{num}
            atom_counter = 0
            for j, line in enumerate(geom_content):
                spl = line.split()

                if 'atom' and target_atom in line:
                    if atom_counter == i:
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
                    continue

                # Some error checking
                elif 'restart' == spl[0]:
                    print('restart keyword already found in control.in')
                    exit(1)
                elif 'charge' == spl[0]:
                    print('charge keyword already found in control.in')
                    exit(1)

                # Fix basis sets
                elif 'species' == spl[0] and target_atom == spl[1]:
                    if found_target_atom is False:
                        control_content[j] = f'  species        {target_atom}1'
                        found_target_atom = True

                # Change keyword lines
                elif 'sc_iter_limit' in spl:
                    control_content[j] = iter_limit
                elif 'sc_init_iter' in spl:
                    control_content[j] = init_iter
                elif 'KS_method' in spl:
                    control_content[j] = ks_method
                elif 'restart_write_only' in spl:
                    control_content[j] = restart_file
                elif 'restart_save_iterations' in spl:
                    control_content[j] = restart_save
                elif 'force_single_restartfile' in spl:
                    control_content[j] = restart_force
                elif '#charge' in spl:
                    control_content[j] = charge
                elif '#' == spl[0] and 'charge' == spl[1]:
                    control_content[j] = charge
                elif 'output' == spl[0] and 'mulliken' == spl[1]:
                    control_content[j] = output_mull
                elif 'output' == spl[0] and 'hirshfeld' == spl[1]:
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

    print('init files written successfully')


def create_hole_files(target_atom, num_atom):
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

                if len(spl) > 1:
                    continue

                # Some error checking
                elif 'sc_init_iter' == spl[0]:
                    print('sc_init_iter keyword already found in init/control.in')
                    exit(1)
                elif 'restart_read_only' == spl[0]:
                    print('restart_read_only keyword already found in init/control.in')
                    exit(1)
                elif 'force_occupation_projector' == spl[0]:
                    print('force_occupation_projector keyword already found in init/control.in')
                    exit(1)
                elif 'output' == spl[0] and 'cube' == spl[1] and 'spin_density' == spl[2]:
                    print('output cube spin_density already found in init/control.in')
                    exit(1)
                elif 'output' == spl[0] and 'mulliken' == spl[1]:
                    print('output mulliken already found in init/control.in')
                    exit(1)
                elif 'output' == spl[0] and 'hirshfeld' == spl[1]:
                    print('output hirshfeld already found in init/control.in')
                    exit(1)

                # Change keyword lines
                elif 'sc_iter_limit' in spl:
                    control_content[j] = iter_limit
                elif '#sc_init_iter' in spl:
                    control_content[j] = init_iter
                elif '#' == spl[0] and 'sc_init_iter' == spl[1]:
                    control_content[j] = init_iter
                elif 'KS_method' in spl:
                    control_content[j] = ks_method
                elif 'restart' == spl[0]:
                    control_content[j] = restart
                elif '#force_occupation_projector' == spl[0]:
                    control_content[j] = fop
                elif '#' == spl[0] and 'force_occupation_projector' == spl[1]:
                    control_content[j] = fop
                elif 'charge' in spl:
                    control_content[j] = charge
                elif ['#output', 'cube', 'spin_density'] == spl or ['#', 'output', 'cube', 'spin_density'] == spl:
                    control_content[j] = output_cube
                elif ['#output', 'hirshfeld'] == spl or ['#', 'output', 'hirshfeld'] == spl:
                    control_content[j] = output_hirsh
                elif ['#output', 'mulliken'] == spl or ['#', 'output', 'mulliken'] == spl:
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
    create_init_files(target_atom, num_atom)
    create_hole_files(target_atom, num_atom)
