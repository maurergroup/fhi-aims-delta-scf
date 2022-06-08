#!/usr/bin/env python3

import glob
import shutil


def copy_restart():
    atom = str(input('Enter atom: '))

    for dir in glob.glob(f'{atom}*'):
        for restart in glob.glob('/init/restart_file*'):
            shutil.copyfile(f'{dir}/init/{restart}',
                            f'{dir}/hole/{restart}')


if __name__ == "__main__":
    copy_restart()
