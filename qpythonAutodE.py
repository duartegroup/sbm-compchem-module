#!/usr/bin/env python3
import os
import argparse
import shutil


def get_args():
    """Get the command line arguments passed to this script using argparse"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        action='store',
                        type=str,
                        help='.py file submit to the queue')

    parser.add_argument("-np", "--num_processors",
                        type=int,
                        default=1,
                        help="Number of cores to use. Default: 1")

    parser.add_argument('-omp', '--omp_num_threads',
                        type=int,
                        default=1,
                        help='Number of OMP threads to use. Default: 1')

    parser.add_argument("-args", '--extra_arguments',
                        type=str,
                        help='Extra arguments to parse to the python script',
                        default='')

    return parser.parse_args()



if __name__ == '__main__':

    args = get_args()
    if not args.filename.endswith('.py'):
        exit(f'Filename must end with .py. Had: {args.filename}')

    script_filename = args.filename.replace('.py', '.sh')

    if script_filename[0].isdigit():  # Scripts can't start with a digit...
        script_filename = f'_{script_filename}'

    with open(script_filename, 'w') as sub_script:
        print('#!/bin/bash',
              '#$ -cwd',
              f'#$ -pe smp {max(args.num_processors, 1)}',
              '#$ -l s_rt=360:00:00',
              f'export OMP_NUM_THREADS={max(args.omp_num_threads, 1)}',
              'module load openmpi4.1.1',
              'export PATH="/usr/local/orca_5_0_4/:$PATH"',
              'source ~/miniconda3/bin/activate',
              'conda activate /usr/local/conda/envs/autode',
              ' ',
              f'/usr/local/conda/envs/autode/bin/python {args.filename} {args.extra_arguments}',
              sep='\n', file=sub_script)

    os.system(f'qsub {script_filename}')
