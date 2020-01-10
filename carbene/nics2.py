from __future__ import print_function
import sys
import os
import platform

if platform.python_version().startswith("2"):
    sys.exit("") # Python 2
else:
    try:
        import numpy as np
    except:
        sys.exit("Please make sure you have numpy installed.")

    print("\nInput total shielding tensor: \n")
    stens = []
    line = "test"
    while len(stens) < 3:
        line = input()
        if line:
            sval = [float(i.strip()) for i in line.split()]
            stens.append(sval)

    # s: Shielding tensor
    s = np.array(stens)
    # paxes: Principal axes of shielding tensor. 
    #        i.e. the matrix containing (column) eigenvectors of s.' * s (in MATLAB notation)
    _, paxes = np.linalg.eig(np.matmul(np.transpose(s), s))
    # pval: Principal values of shielding tensor
    pval = np.diag(np.matmul(np.matmul(np.transpose(paxes), s), paxes)) # Matrix multiplication is associative...

    print("\nInput coordinates of three atoms in the ring (in the format ATOM  xcoord   ycoord   zcoord): \n")
    line = input()
    c = [float(i.strip()) for i in line.split()[1:]]
    c1 = np.array(c)
    line = input()
    c = [float(i.strip()) for i in line.split()[1:]]
    c2 = np.array(c)
    line = input()
    c = [float(i.strip()) for i in line.split()[1:]]
    c3 = np.array(c)

    # Calculate unit vector normal to the plane.
    n = np.cross(c1 - c2, c1 - c3)
    n = n/np.linalg.norm(n)

    # Calculate inner product of n with each principal axis.
    d = np.matmul(np.transpose(paxes), n)
    # The principal axis with the largest absolute value of the dot product is the 'zz' axis.
    maxd = np.argmax(np.abs(d))
    # NICS0_zz value is the principal value corresponding to this axis (but with sign flipped, because convention)
    nics = -pval[maxd]
    print("\n===============================")
    print("   NICS0_zz value: %.4f" % nics)
    print("===============================\n")

