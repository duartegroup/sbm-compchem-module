"""
Script to generate a 2D surface figure from an ORCA output file


Written by T. Young 2019 with code from autode written by T Young/J Silcock
"""
import argparse
import numpy as np
from numpy.polynomial import polynomial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FormatStrFormatter


def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', type=str, help='ORCA .out file')

    return parser.parse_args()


def polyfit2d(x, y, z, order=5):
    """Takes x and y coordinates and their resultant z value, and creates a matrix where element i,j is the coefficient
    of the desired order polynomial x ** i * y ** j

    Arguments:
        x {np.array} -- flat array of x coordinates
        y {np.array} -- flat array of y coordinates
        z {np.array} -- flat array of z value at the corresponding x and y value
        order {int} -- max order of polynomial to work out

    Returns:
        np.array -- matrix of polynomial coefficients
    """
    deg = np.array([order, order])
    vander = polynomial.polyvander2d(x, y, deg)
    # vander matrix is matrix where each row i deals with x=x[i] and y=y[i], and each item in the
    # row has value x ** m * y ** n with (m,n) = (0,0), (0,1), (0,2) ... (1,0), (1,1), (1,2) etc up to (order, order)
    coeff_mat, _, _, _ = np.linalg.lstsq(vander, z, rcond=None)
    return coeff_mat.reshape(deg + 1)


def get_rs_energies(output_file_lines):
    """
    Get the distances and energies from the 2D ORCA output file

    :param output_file_lines: (list(str))
    :return: (list(tuple)), (list(float))
    """
    print('Extracting data')

    r1s, r2s, energies = [], [], []
    energies_section = False
    for n, line in enumerate(reversed(output_file_lines)):
        if n > 2:
            if 'The Calculated Surface using the SCF energy' in output_file_lines[len(output_file_lines)-n+1]:
                energies_section = True

        if "The Calculated Surface using the 'Actual Energy'" in line:
            break

        if energies_section:
            r1, r2, energy = line.split()
            r1s.append(float(r1))
            r2s.append(float(r2))
            energies.append(float(energy))

    rel_energies = [627.5*(e - min(energies)) for e in energies]

    return r1s, r2s, rel_energies


def plot_figure(output_file_lines):

    r1s, r2s, es = get_rs_energies(output_file_lines)

    print('Plotting figure...')
    coeff_mat = polyfit2d(r1s, r2s, es)

    nx, ny = 20, 20
    xx, yy = np.meshgrid(np.linspace(min(r1s), max(r1s), nx),
                         np.linspace(min(r2s), max(r2s), ny))

    zz = polynomial.polyval2d(xx, yy, coeff_mat)
    fig = plt.figure(figsize=(10, 3.5))
    plt.subplots_adjust(wspace=0.4)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax1.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
    pos1 = ax1.plot_surface(xx, yy, zz, cmap=plt.get_cmap('plasma'), alpha=0.9)
    pos1 = ax1.contour3D(xx, yy, zz, 30, colors='k', antialiased=True)
    ax1.view_init(45)
    ax1.set_xlabel('$r_1$ / Å')
    ax1.set_ylabel('$r_2$ / Å')

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_xlabel('$r_1$ / Å')
    ax2.set_ylabel('$r_2$ / Å')
    pos2 = ax2.imshow(zz, aspect='equal', extent=(min(r1s), max(r1s), min(r2s), max(r2s)), origin='lower',
                      cmap=plt.get_cmap('plasma'))
    cbar2 = plt.colorbar(pos2, ax=ax2)
    cbar2.set_label('∆$E$ / kcal mol$^{-1}$', rotation=270, labelpad=15)

    # plt.show()
    plt.savefig('surface', dpi=1000)

    print('Done!')
    return None


if __name__ == '__main__':

    args = get_args()

    # Check that the file is a .out
    if not args.filename.endswith('.out'):
        exit('ORCA output file must be a .out. Exiting')

    file_lines = open(args.filename, 'r', encoding="utf-8", errors="ignore").readlines()

    # Check that the ORCA calculation is of the correct sort
    correct_file_type = True if 'There are 2 parameter to be scanned' in ''.join(file_lines[:200]) else False
    correct_file_type = True if 'There are 2 parameter(s) to be scanned' in ''.join(file_lines[:200]) else False

    if not correct_file_type:
        exit('ORCA output file was not of the correct format. Exiting')

    plot_figure(output_file_lines=file_lines)
