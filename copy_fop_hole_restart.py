#!/usr/bin/env python3

import glob
import shutil


def copy_restart():
    atom = str(input('Enter atom: '))

    for dir in glob.glob(f'{atom}*'):
        shutil.copyfile(f'{dir}/init/restart_file',
                        f'{dir}/hole/restart_file')


if __name__ == "__main__":
    copy_restart()
