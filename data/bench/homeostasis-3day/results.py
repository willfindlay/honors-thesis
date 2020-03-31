#! /usr/bin/env python3

import os, sys
import re
import functools

import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
sns.set_palette(flatui)

def parse_syscall_results(f):
    data = []
    data = pd.read_csv(f, sep=r'\s+', skiprows=5, header=0)
    try:
        data.columns = ['syscall', 'count', 'dummy', 'time']
        #data = data[['syscall', 'count', 'time']]
    except ValueError:
        data.columns = ['syscall', 'count', 'time']
        data['time'] = data['time'] / data['count']
    return data

def parse_results_file(f):
    if 'base' in f:
        ftype = 'base'
    elif 'ebph' in f:
        ftype = 'ebph'
    else:
        raise Exception(f'{f} does not contain "base" or "ebph"')
    data = parse_syscall_results(f)
    return (ftype, data)

def parse_all_results(d):
    base = []
    ebph = []
    for f in sorted(os.listdir(d)):
        f = os.path.join(d, f)
        fname, dfs = parse_results_file(f)
        if fname == 'base':
            base.append(dfs)
        else:
            ebph.append(dfs)
    base = combine_data(base)
    ebph = combine_data(ebph)
    return base, ebph

def combine_data(data):
    combined = pd.concat(data)
    #combined = discard_outliers(combined, 3)
    combined = combined.groupby('syscall', as_index=False).agg({'count': 'sum', 'time': [ 'mean', 'std', 'sem']})
    combined.columns = ['_'.join(col).strip('_') for col in combined.columns.values]
    combined = combined.rename(columns={'count_sum': 'count'})
    return combined

#def discard_outliers(data, stds):
#    z = data[['syscall', 'time', 'dummy']].groupby('syscall').transform(lambda g: (g - g.mean()).div(g.std()))
#    outliers = z.abs() > stds
#    data = data[~outliers.any(axis=1)]
#    return data

def compare(base, ebph):
    data = pd.merge(base, ebph, on='syscall', suffixes=['_base', '_ebph'])
    data['count'] = data['count_base'] + data['count_ebph']
    data = data.drop(columns=['count_base', 'count_ebph'])
    data['diff'] = (data['time_mean_ebph'] - data['time_mean_base'])
    data['overhead'] = data['diff'] / data['time_mean_base'] * 100
    # Outlier stuff
    data = data[(np.abs(sp.stats.zscore(data['time_mean_base'])) < 3)]
    data = data[(np.abs(sp.stats.zscore(data['time_mean_ebph'])) < 3)]
    data = data[(np.abs(sp.stats.zscore(data['overhead'])) < 3)]
    data = data[(np.abs(sp.stats.zscore(data['diff'])) < 3)]
    return data

def export_all(data):
    export_data(data, 'homeostasis_3day')

def export_data(orig, prefix):
    # Make table --------------------------------------------------------
    data = orig.copy()

    # Get top 20 by count
    data = data.sort_values('count', ascending=0)
    data = data[:20]

    # Format table
    column_format = r'>{\ttfamily}lrrrrr'
    data['time_base'] = data['time_mean_base'].map('{:.3f} '.format) + \
            data['time_std_base'].map('({:.4f})'.format)
    data['time_ebph'] = data['time_mean_ebph'].map('{:.3f} '.format) + \
            data['time_std_ebph'].map('({:.4f})'.format)
    data = data[['syscall', 'count', 'time_base', 'time_ebph', 'diff', 'overhead']]
    data['syscall'] = data['syscall'].str.replace('_', r'\_')
    data = data.rename(columns={
        'syscall': r'\multicolumn{1}{l}{System Call}',
        'count': r'Count',
        'time_base': r'$T_\text{base}$ ($\mu$s)',
        'time_ebph': r'$T_\text{ebpH}$ ($\mu$s)',
        'diff':r'Diff. ($\mu$s)',
        'overhead':r'\% Overhead',
        })
    data.to_latex(index=0, escape=0, buf=f'{prefix}_results.tex', column_format=column_format)

    # Make figure -------------------------------------------------------
    data = orig.copy()

    # Get top 20 by count
    data = data.sort_values('count', ascending=0)
    data = data[:20]

    # Plot
    plot = data.plot(yerr={'time_mean_base': data['time_sem_base'], 'time_mean_ebph': data['time_sem_ebph']},
            y=['time_mean_base', 'time_mean_ebph'],
            x='syscall',
            kind='bar',
            capsize=2,
            logy=True,
            )
    plot.set_xlabel('System Call')
    plot.set_ylabel(r"Time ($\mu$s)")
    plot.legend(['Base', 'ebpH'])
    plot.get_figure().savefig(f'{prefix}_times.png', bbox_inches='tight', dpi=200)

base, ebph = parse_all_results('results')
data = compare(base, ebph)
export_all(data)
