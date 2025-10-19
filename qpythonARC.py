#!/usr/bin/env python3
import os
import argparse


def get_args():
    """Get the command line arguments passed to this script using argparse"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        action='store',
                        help='.py file submit to the queue',
                        type=str)

    parser.add_argument("-np", "--num_processors",
                        type=int,
                        default=0,
                        help="Specify the number of cores")
    
    parser.add_argument("--partition",
                        action='store',
                        default=False,
                        help="Which ARC partition to submit the jobs to. Valid "
                             "options are short, medium, long, and devel. If "
                             " not specified, defaults to long")
    
    parser.add_argument("--clusters",
                        action='store',
                        default=False,
                        help="Which cluster to submit: [htc | arc | all]")
    
    parser.add_argument("--priority",
                        action='store_true',
                        default=False,
                        help="Whether to consume priority time. Be careful!")
    
    parser.add_argument("-p", "--only_print",
                        action='store_true',
                        default=False,
                        help="Only print the submit script, do not submit it. "
                            "Useful for debugging and editing script before "
                            "submission.")
    
    parser.add_argument("-t", "--time",
                        action='store',
                        default="2-00:00:00",
                        help='Specify the runtime for the job, in format [d-]hh:mm:ss')

    parser.add_argument("-args", '--extra_arguments',
                        type=str,
                        help='Extra arguments to parse to the python script',
                        default='')
    
    return parser.parse_args()



def print_sub_script(sh_filename, inp_filename, args):
    """
    Print the submission script appropriate for an ORCA input file

    -------------------------------------------------------------
    Arguments:
        sh_filename (str): Submission script filename
        inp_filename (str): Input filename
        args (Namespace): Command line arguments
    """

    with open(sh_filename, 'w') as sub_script:
        print('#!/bin/bash',
              f'#SBATCH --ntasks-per-node={args.num_processors}',
              f'#SBATCH --time={args.time}',
              f'#SBATCH --job-name={inp_filename[:-3]}',
              sep='\n', file=sub_script)
        if args.clusters:
            print(f'#SBATCH --clusters={args.clusters}', file=sub_script)
        if args.partition:
            print(f'#SBATCH --partition={args.partition}', file=sub_script)
        if args.priority:
            print(f'#SBATCH --qos=priority', file=sub_script)

        print('module load ORCA/5.0.4-gompi-2021b',
              "export OMPI_MCA_pml='ucx'",  ## temporary fix for ARC issue
              "export OMPI_MCA_btl='^uct,ofi'",
              "export OMPI_MCA_mtl='^ofi'",
              "",
              f"conda activate {os.environ['CONDA_DEFAULT_ENV']}",
              f"python {args.filename} {args.extra_arguments} > {args.filename[:-3]+'.log'}",
               sep='\n', file=sub_script)

    return None


if __name__ == '__main__':

    arguments = get_args()

    filename = arguments.filename
    
    if not filename.endswith('.py'):
        exit(f'Filename must end with .py. Found: {filename}')

    script_filename = filename.replace('.py', '.sh')

    # The queuing system cannot work with scripts starting with a digit...
    if script_filename[0].isdigit():
        script_filename = f'_{script_filename}'

    print_sub_script(script_filename,
                        inp_filename=filename,
                        args=arguments)

    if not arguments.only_print:
        os.system(f'sbatch {script_filename}')
