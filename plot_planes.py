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
    fdir = os.path.abspath('HybridWALE')
    sdir = os.path.join(fdir, 'slices')
    pattern = '*99.csv'
    yname = os.path.join(fdir, 'mcalisterWing.i')

    edir = os.path.abspath('exp_data')
    fux_exp = os.path.join(edir, 'ux_x4.txt')
    fuz_exp = os.path.join(edir, 'uz_x4.txt')

    ninterp = 100
    mm2ft = 0.003281

    # ========================================================================
    # Read in data
    fnames = sorted(glob.glob(os.path.join(sdir, pattern)))
    df = get_merged_csv(fnames)
    renames = {'Points:0': 'x',
               'Points:1': 'y',
               'Points:2': 'z',
               'pressure': 'p',
               'velocity_:0': 'ux',
               'velocity_:1': 'uy',
               'velocity_:2': 'uz'}
    df.columns = [renames[col] for col in df.columns]

    # simulation setup parameters
    u0, rho0, mu = parse_ic(yname)
    chord = 1

    # ========================================================================
    # Lineout through vortex core in each slice
    xslices = np.unique(df['x'])

    for k, xslice in enumerate(xslices):
        subdf = df[df['x'] == xslice]
        idx = subdf['p'].idxmin()
        ymin, ymax = np.min(subdf['y']), np.max(subdf['y'])
        zmin, zmax = np.min(subdf['z']), np.max(subdf['z'])

        # vortex center location
        yc = np.array([subdf['y'].loc[idx]])
        zc = np.array([subdf['z'].loc[idx]])

        # interpolate across the vortex core
        yline = np.linspace(ymin, ymax, ninterp)
        zline = np.linspace(zmin, zmax, ninterp)
        ux_zc = spi.griddata((subdf['y'], subdf['z']), subdf['ux'],
                             (yline[None, :], zc[:, None]), method='cubic')
        uz_zc = spi.griddata((subdf['y'], subdf['z']), subdf['uz'],
                             (yline[None, :], zc[:, None]), method='cubic')

        plt.figure(0)
        plt.plot(yline / chord, ux_zc[0, :] / u0, ls='-', lw=2, color=cmap[k])

        plt.figure(1)
        plt.plot(yline / chord, uz_zc[0, :] / u0, ls='-', lw=2, color=cmap[k])

    # # ========================================================================
    # # Operate on each slice
    # xslices = np.unique(df['x'])
    # for k, xslice in enumerate(xslices):
    #     subdf = df[df['x'] == xslice]
    #     ymin, ymax = np.min(subdf['y']), np.max(subdf['y'])
    #     zmin, zmax = np.min(subdf['z']), np.max(subdf['z'])
    #     yi = np.linspace(ymin, ymax, ninterp)
    #     zi = np.linspace(zmin, zmax, ninterp)

    #     pi = spi.griddata((subdf['y'], subdf['z']), subdf['p'],
    #                       (yi[None, :], zi[:, None]), method='cubic')

    #     plt.figure(k + 100)
    #     CS = plt.contourf(yi, zi, pi, 15, cmap=plt.cm.jet)
    #     plt.colorbar()
    #     plt.xlim(ymin, ymax)
    #     plt.ylim(zmin, zmax)

    # ========================================================================
    # Experimental data
    exp_ux_df = pd.read_csv(fux_exp, delimiter=',',
                            header=0, names=['y', 'ux'])
    exp_uz_df = pd.read_csv(fuz_exp, delimiter=',',
                            header=0, names=['y', 'uz'])

    exp_ux_df['y'] = exp_ux_df['y'] * mm2ft / chord
    exp_uz_df['y'] = exp_uz_df['y'] * mm2ft / chord

    plt.figure(0)
    plt.plot(exp_ux_df['y'], exp_ux_df['ux'], ls='-', lw=1, color=cmap[-1],
             marker=markertype[0], mec=cmap[-1], mfc=cmap[-1], ms=6)

    plt.figure(1)
    plt.plot(exp_uz_df['y'], exp_uz_df['uz'], ls='-', lw=1, color=cmap[-1],
             marker=markertype[0], mec=cmap[-1], mfc=cmap[-1], ms=6)

    # ========================================================================
    # Save plots
    plt.figure(0)
    ax = plt.gca()
    plt.xlabel(r"$y/c$", fontsize=22, fontweight='bold')
    plt.ylabel(r"$u_x$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('ux.png', format='png')

    plt.figure(1)
    ax = plt.gca()
    plt.xlabel(r"$y/c$", fontsize=22, fontweight='bold')
    plt.ylabel(r"$u_z$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('uz.png', format='png')

    if args.show:
        plt.show()
