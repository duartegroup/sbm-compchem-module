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

    parser.add_argument("-notrashtmp", "--no_trash_tmp",
                        action='store_true',
                        default=False,
                        help="Don't trash the temporary files that may be "
                             "generated.")

    parser.add_argument("-np", "--num_processors",
                        type=int,
                        default=0,
                        help="Override the number of cores specified in the "
                             "input file. Useful for running calculations "
                             "with >4 GB memory per core.")
    
    parser.add_argument("--partition",
                        action='store',
                        default=False,
                        help="Which ARC partition to submit the jobs to. Valid "
                             "options are short, medium, long, and devel")
    
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
                        required=True,
                        help='Specify the runtime for the job, in format [d-]hh:mm:ss')
    
    return parser.parse_args()


def num_cores(inp_filename, args):
    """
    Get the number of cores that this input file will need

    Returns:
        (int): Number of cores

    Raises:
        (ValueError, IndexError): If the input file is malformatted
    """
    _num_cores = 1   # Default value
    
    fh = open(inp_filename, 'r')
    # Number of cores can be defined with PALX in the keyword line
    for line in fh:
        if line.startswith('!'):
            for item in line.split():
                if item.strip().lower().startswith('pal'):
                    _num_cores = int(item[3:])
    
    # Can also have a %pal directive in the input file
    fh.seek(0)
    for line in fh:
        line = line.lower()
        if 'nprocs' in line:
            # expecting an ... nprocs X ... format to the line
            idx = next(i for i, item in enumerate(line.split())
                       if 'nprocs' == item)
            _num_cores = int(line.split()[idx+1])
    fh.close()

    # Command line argument overrides whatever is found
    if args.num_processors != 0:
        _num_cores = args.num_processors

    return _num_cores
    
    
def get_extra_input_files(inp_filename):
    """
    Get a list of extra filenames that have to be copied
    from the current working directory (not exhaustive and
    may miss files)
    """
    # recognized extensions of additional files
    input_exts = (".xyz", ".hess", ".gbw", ".opt")
    file_list = []

    # tokenize the input file
    fh = open(inp_filename, 'r')
    for line in fh:
        for word in line.strip().split():
            word = word.strip('"')
            # check if the file actually exists to prevent bash errors
            if word.endswith(input_exts):
                if not os.path.isfile(word):
                    print(f"WARNING - cannot find {word}")
                    continue
                file_list.append(word)
    fh.close()

    return file_list


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
              f'#SBATCH --ntasks-per-node={num_cores(inp_filename, args)}',
              f'#SBATCH --time={args.time}',
              f'#SBATCH --job-name={inp_filename[:-4]}',
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
              "export ORIG=$PWD",
              "export SCR=$TMPDIR/$SLURM_JOB_ID",
              "mkdir -p $SCR",
               sep='\n', file=sub_script)
        if args.copy_all:
            print('cp * $SCR', file=sub_script)
        else:
            to_copy = get_extra_input_files(inp_filename)
            to_copy.append(inp_filename)
            print('cp', *to_copy, '$SCR', file=sub_script)


        print(f'cd $SCR',
              f'$EBROOTORCA/orca {inp_filename} > {inp_filename.replace(".inp", ".out")}',
              sep='\n', file=sub_script)

        if not args.no_trash_tmp:
            print('rm -f *.tmp', file=sub_script)

        if args.copy_scratch:
            print('cp -R * $ORIG', file=sub_script)
        else:
            # By default only copy back the structure (.xyz) and output (.out)
            # and hessian (*.hess) files; also copy back error file if not empty
            print('cp *.xyz *.out *.hess $ORIG', file=sub_script)

        # Return to the working directory and exit
        print('cd $ORIG', file=sub_script)
        print('rm -r $SCR', file=sub_script)

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

        if not arguments.only_print:
            os.system(f'sbatch {script_filename}')
