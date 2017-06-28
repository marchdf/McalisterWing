#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import pandas as pd
import scipy.interpolate as spi
import yaml

# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc('text', usetex=True)
plt.rc('font', family='serif', serif='Times')
cmap_med = ['#F15A60', '#7AC36A', '#5A9BD4', '#FAA75B',
            '#9E67AB', '#CE7058', '#D77FB4', '#737373']
cmap = ['#EE2E2F', '#008C48', '#185AA9', '#F47D23',
        '#662C91', '#A21D21', '#B43894', '#010202']
dashseq = [(None, None), [10, 5], [10, 4, 3, 4], [
    3, 3], [10, 4, 3, 4, 3, 4], [3, 3], [3, 3]]
markertype = ['s', 'd', 'o', 'p', 'h']


# ========================================================================
#
# Function definitions
#
# ========================================================================
def get_merged_csv(fnames, **kwargs):
    lst = []
    for fname in fnames:
        try:
            df = pd.read_csv(fname, **kwargs)
            lst.append(df)
        except pd.errors.EmptyDataError:
            pass
    return pd.concat(lst, ignore_index=True)


def parse_ic(fname):
    """Parse the Nalu yaml input file for the initial conditions"""
    with open(fname, 'r') as stream:
        try:
            dat = yaml.load(stream)
            u0 = float(dat['realms'][0]['initial_conditions']
                       [0]['value']['velocity'][0])
            rho0 = float(dat['realms'][0]['material_properties']
                         ['specifications'][0]['value'])
            mu = float(dat['realms'][0]['material_properties']
                       ['specifications'][1]['value'])

            return u0, rho0, mu

        except yaml.YAMLError as exc:
            print(exc)


def sort_by_angle(x, y, var):
    """Radial sort of variable on x and y for plotting

    Inspired from:
    http://stackoverflow.com/questions/35606712/numpy-way-to-sort-out-a-messy-array-for-plotting

    """

    # Get the angle wrt the mean of the cloud of points
    x0, y0 = x.mean(), y.mean()
    angle = np.arctan2(y - y0, x - x0)

    # Sort based on this angle
    idx = angle.argsort()
    idx = np.append(idx, idx[0])

    return x[idx], y[idx], var[idx]


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == '__main__':

    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(description='A simple plot tool')
    parser.add_argument(
        '-s', '--show', help='Show the plots', action='store_true')
    args = parser.parse_args()

    # ========================================================================
    # Setup
    ninterp = 100
    mm2ft = 0.003281

    fdir = os.path.abspath('DES')
    yname = os.path.join(fdir, 'mcalisterWing64M.i')
    fname = 'avg_slice.csv'
    sdirs = ['wing_slices64M',
             'wing_slices64M_shifted',
             'wing_slices300M_shifted',
             'wing_slices64M_nso',
             'wing_slices300M_nso']
    labels = ['DES 64M',
              'DES shifted 64M',
              'DES shifted 300M',
              'LES-NSO 64M',
              'LES-NSO 300M']

    # simulation setup parameters
    u0, rho0, mu = parse_ic(yname)
    chord = 1

    # ========================================================================
    # Loop on data directories
    for i, sdir in enumerate([os.path.join(fdir, sdir) for sdir in sdirs]):

        # ========================================================================
        # Read in data
        df = pd.read_csv(os.path.join(sdir, fname), delimiter=',')
        renames = {'Points:0': 'x',
                   'Points:1': 'y',
                   'Points:2': 'z',
                   'pressure': 'p',
                   'pressure_force_:0': 'fpx',
                   'pressure_force_:1': 'fpy',
                   'pressure_force_:2': 'fpz',
                   'tau_wall': 'tau_wall',
                   'velocity_:0': 'ux',
                   'velocity_:1': 'uy',
                   'velocity_:2': 'uz',
                   'time': 'avg_time'}
        df.columns = [renames[col] for col in df.columns]

        # Calculate the negative of the surface pressure coefficient
        df['cp'] = - df['p'] / (0.5 * rho0 * u0**2)

        # ========================================================================
        # Plot cp in each slice
        yslices = np.unique(df['y'])

        for k, yslice in enumerate(yslices):
            subdf = df[df['y'] == yslice]

            # Sort for a pretty plot
            x, z, cp = sort_by_angle(np.array(subdf['x']),
                                     np.array(subdf['z']),
                                     np.array(subdf['cp']))

            # plot
            plt.figure(k)
            ax = plt.gca()
            p = plt.plot(x / chord, cp, ls='-', lw=2,
                         color=cmap[i], label=labels[i])
            p[0].set_dashes(dashseq[i])

    # ========================================================================
    # Save plots
    for k, yslice in enumerate(yslices):
        plt.figure(k)
        ax = plt.gca()
        plt.xlabel(r"$x/c$", fontsize=22, fontweight='bold')
        plt.ylabel(r"$-c_p$", fontsize=22, fontweight='bold')
        plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight='bold')
        plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight='bold')
        plt.xlim([0, chord])
        plt.ylim([-1.5, 4.5])
        plt.tight_layout()
        if (k == 1):
            legend = ax.legend(loc='best')
        plt.savefig('cp_{0:f}.png'.format(yslice), format='png')

    if args.show:
        plt.show()
