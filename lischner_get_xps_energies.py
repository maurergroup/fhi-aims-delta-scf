#!/usr/bin/env python3

import os


def read_ground():
    """Get the ground state energy."""
    with open('ground/aims.out', 'r') as ground:
        for line in ground:

            # Get the energy
            if 's.c.f. calculation      :' in line:
                grenrgys = float(get_energy_level(line))

    print('Ground state calculated energy (eV):')
    print(grenrgys)
    print()

    return grenrgys


def get_energy_level(line):
    """Check for a float in a line in a file."""
    for word in line.split():
        try:
            return float(word)
        except ValueError:
            pass


def contains_number(string):
    """Check if a number is in a string."""
    for character in string:
        if character.isdigit():
            return True

    return False


def read_atoms(get_energy_level, contains_number):
    """Get the excited state energies."""
    dir_list = os.listdir('./')
    element = str(input('Enter atom: '))
    energy = 's.c.f. calculation      :'
    excienrgys = []

    # Read each core hole dir
    for directory in dir_list:
        if element in directory and contains_number(directory) is True:

            with open(directory + '/hole/aims.out', 'r') as out:
                for line in out:

                    # Get the energy
                    if energy in line:
                        excienrgys.append(get_energy_level(line))

    print('Core hole calculated energies (eV):', *excienrgys, sep='\n')

    return element, excienrgys


def calc_delta_scf(element, grenrgys, excienrgys):
    """Calculate delta scf and write to a file."""
    xps = []

    for i in excienrgys:
        xps.append(i - grenrgys)

    with open(element + '_xps_peaks.txt', 'w') as file:
        for i in xps:
            file.write(f'{i}\n')


if __name__ == '__main__':
    grenrgys = read_ground()
    element, excienrgys = read_atoms(get_energy_level, contains_number)
    calc_delta_scf(element, grenrgys, excienrgys)
