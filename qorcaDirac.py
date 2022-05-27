#!/usr/bin/env python3
import os
import argparse


def get_args():
    """Get the command line arguments passed to this script using argparse"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.inp file(s) submit to the queue',
                        nargs='+')

    parser.add_argument("-ca", "--copy_all",
                        action='store_true',
                        default=False,
                        help='Copy all of the files in the current directory '
                             'to the compute node.')

    parser.add_argument("-cs", "--copy_scratch",
                        action='store_true',
                        default=False,
                        help="Copy all files from the scratch directory back "
                             "to this directory when the calculation is "
                             "finished.")

    parser.add_argument('-v', '--version',
                        action='store',
                        type=str,
                        choices=['4_1', '4_2'],
                        default='4_2',
                        help="Which version of ORCA should be used for the "
                             "calculation? Default: 4.2.1")

    parser.add_argument("-np", "--num_processors",
                        type=int,
                        default=0,
                        help="Override the number of cores specified in the "
                             "input file. Useful for running calculations "
                             "with >4 GB memory per core.")

    return parser.parse_args()


def num_cores(inp_filename, args):
    """Get the number of cores that this input file will need

    Returns:
        (int): Number of cores

    Raises:
        (ValueError, IndexError): If the input file is malformatted
    """
    _num_cores = 1   # Default value

    try:
        keyword_line = next(line for line in open(inp_filename, 'r')
                            if line.startswith('!'))

        # Number of cores can be defined with PALX in the keyword line
        for item in keyword_line.split():
            if item.lower().startswith("pal"):
                _num_cores = int(item[3:])

    except StopIteration:
        exit(f'{inp_filename} was not a correctly formatted. Must have a '
             f'line starting with a !')

    # Could also have a %pal directive in the input file...
    for line in open(inp_filename, 'r'):

        if 'nprocs' in line:
            # expecting a ... nprocs X ... format to the line
            idx = next(i for i, item in enumerate(line.split())
                       if 'nprocs' == item.lower())

            _num_cores = int(line.split()[idx+1])

    # Command line argument overrides whatever is found
    if args.num_processors != 0:
        _num_cores = args.num_processors

    return _num_cores


def print_sub_script(sh_filename, inp_filename, args):
    """
    Print the submission script appropriate for an ORCA input file

    -------------------------------------------------------------
    Arguments:
        sh_filename (str): Submission script filename
        inp_filename (str): Input filename
        args (Namespace): Command line arguments
    """

    if args.version == '4_1':
        orca_path = '/usr/local/orca_4_1_1_linux_x86-64/orca'
    elif args.version == '4_2':
        orca_path = '/usr/local/orca_4_2_1_linux_x86-64/orca'
    else:
        exit(f"{args.version} is not a recognised ORCA version")

    with open(sh_filename, 'w') as sub_script:
        print('#!/bin/csh',
              '#$ -cwd',
              f'#$ -pe smp {num_cores(inp_filename, args)}',
              '#$ -l s_rt=360:00:00',
              '#',
              'setenv ORIG $PWD',
              'setenv SCR $TMPDIR',
              'module load mpi/openmpi3-x86_64',
              f'cp {"*" if args.copy_all else inp_filename} $SCR',
              f'cd $SCR',
              f'{orca_path} {inp_filename} > {inp_filename.replace(".inp", ".out")}',
              'rm -f *.tmp',
              sep='\n', file=sub_script)

        if args.copy_scratch:
            print('cp -R * $ORIG', file=sub_script)
        else:
            print('cp *.xyz *.hess *.out $ORIG', file=sub_script)

        print('rm *.sh.*', file=sub_script)

    return None


if __name__ == '__main__':

    arguments = get_args()

    for filename in arguments.filenames:
        if not filename.endswith('.inp'):
            exit(f'Filename must end with .inp. Found: {filename}')

        script_filename = filename.replace('.inp', '.sh')

        # The queuing system cannot work with scripts starting with a digit...
        if script_filename[0].isdigit():
            script_filename = f'_{script_filename}'

        print_sub_script(script_filename,
                         inp_filename=filename,
                         args=arguments)

        os.system(f'qsub {script_filename}')

