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
import matplotlib as mpl
mpl.use('Agg')
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
    ninterp = 200
    mm2ft = 0.003281

    fdir = os.path.abspath('DES')
    yname = os.path.join(fdir, 'mcalisterWing64M.i')
    fname = 'avg_slice.csv'
    # sdirs = ['vortex_slices64M',
    #          'vortex_slices64M_shifted',
    #          'vortex_slices64M_nso']
    # labels = ['DES 64M',
    #           'DES shifted 64M',
    #           'LES-NSO 64M']
    # sdirs = ['vortex_slices64M_shifted',
    #          'vortex_slices300M_shifted']
    # labels = ['DES shifted 64M',
    #           'DES shifted 300M']
    sdirs = ['vortex_slices64M',
             'vortex_slicesRC64M']
    labels = ['DES 64M',
              'DES RC 64M']

    edir = os.path.abspath('exp_data')
    fux_exp = os.path.join(edir, 'ux_x4.txt')
    fuz_exp = os.path.join(edir, 'uz_x4.txt')

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
                   'velocity_:0': 'ux',
                   'velocity_:1': 'uy',
                   'velocity_:2': 'uz',
                   'time': 'avg_time'}
        df.columns = [renames[col] for col in df.columns]

        # ========================================================================
        # Lineout through vortex core in each slice
        xslices = np.unique(df['x'])
        xslices = [5]

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
            p = plt.plot(yline / chord, ux_zc[0, :] /
                         u0, ls='-', lw=2, color=cmap[i], label=labels[i])
            p[0].set_dashes(dashseq[i])

            plt.figure(1)
            p = plt.plot(yline / chord, uz_zc[0, :] /
                         u0, ls='-', lw=2, color=cmap[i])
            p[0].set_dashes(dashseq[i])

            # Plot contours
            if i == 0:
                yi = np.linspace(ymin, ymax, ninterp)
                zi = np.linspace(zmin, zmax, ninterp)

                pi = spi.griddata((subdf['y'], subdf['z']), subdf['p'],
                                  (yi[None, :], zi[:, None]), method='cubic')

                plt.figure(k + 100)
                CS = plt.contourf(yi, zi, pi, 15, cmap=plt.cm.jet)
                plt.colorbar()
                plt.xlim(ymin, ymax)
                plt.ylim(zmin, zmax)

    # ========================================================================
    # Experimental data
    exp_ux_df = pd.read_csv(fux_exp, delimiter=',',
                            header=0, names=['y', 'ux'])
    exp_uz_df = pd.read_csv(fuz_exp, delimiter=',',
                            header=0, names=['y', 'uz'])

    # Shift in ft to align coordinates with mesh.
    yshift = 0.0749174

    exp_ux_df['y'] = (exp_ux_df['y'] * mm2ft - yshift) / chord
    exp_uz_df['y'] = (exp_uz_df['y'] * mm2ft - yshift) / chord

    plt.figure(0)
    plt.plot(exp_ux_df['y'], exp_ux_df['ux'], ls='-', lw=1, color=cmap[-1],
             marker=markertype[0], mec=cmap[-1], mfc=cmap[-1], ms=6, label='Exp.')

    plt.figure(1)
    plt.plot(exp_uz_df['y'], exp_uz_df['uz'], ls='-', lw=1, color=cmap[-1],
             marker=markertype[0], mec=cmap[-1], mfc=cmap[-1], ms=6)

    # ========================================================================
    # Save plots
    plt.figure(0)
    ax = plt.gca()
    plt.xlabel(r"$y/c$", fontsize=22, fontweight='bold')
    plt.ylabel(r"$u_x/u_\infty$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight='bold')
    plt.tight_layout()
    ax.set_xlim([-1, 1])
    legend = ax.legend(loc='best')
    plt.savefig('ux.png', format='png')

    plt.figure(1)
    ax = plt.gca()
    plt.xlabel(r"$y/c$", fontsize=22, fontweight='bold')
    plt.ylabel(r"$u_z/u_\infty$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight='bold')
    plt.tight_layout()
    ax.set_xlim([-1, 1])
    plt.savefig('uz.png', format='png')

    if args.show:
        plt.show()
