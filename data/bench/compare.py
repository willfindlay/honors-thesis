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
flatui = ["#9b59b6", "#3498db", "#6369d1", "#95a5a6", "#34495e", "#2ecc71"]
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

def discard_outliers(data):
    grp = data.groupby('syscall')
    mean = grp['time'].transform('mean')
    std = grp['time'].transform('std')
    zscore = (data['time'] - mean) / std
    zscore = zscore.fillna(0)
    good = zscore < 3
    return data[good]

def combine_data(data):
    combined = pd.concat(data)
    combined = discard_outliers(combined)
    combined = combined.groupby('syscall', as_index=False).agg({'count': 'sum', 'time': [ 'mean', 'std', 'sem']})
    combined.columns = ['_'.join(col).strip('_') for col in combined.columns.values]
    combined = combined.rename(columns={'count_sum': 'count'})
    return combined

def compare(base, ebph):
    data = pd.merge(base, ebph, on='syscall', suffixes=['_base', '_ebph'])
    data['count'] = data['count_base'] + data['count_ebph']
    data = data.drop(columns=['count_base', 'count_ebph'])
    data['diff'] = (data['time_mean_ebph'] - data['time_mean_base'])
    data['overhead'] = data['diff'] / data['time_mean_base'] * 100
    # Discard pathological data
    data = data[data['time_std_base'] < 10]
    data = data[data['time_std_ebph'] < 10]
    return data

def export_data(orig, prefix):
    # Make figure -------------------------------------------------------
    data = orig.copy()

    data = data[data['overhead'] >= 0]

    # Plot
    plot = sns.lmplot('time_mean_base', 'overhead', data=data, hue='system', fit_reg=True,
            logx=True,
            markers=['+', 'x', '.'],
            scatter_kws={'s':20})
    plot.set(xlim=(0, 10), ylim=(0,200))
    plot.set(xlabel=r'Base Time ($\mu$s)')
    plot.set(ylabel=r'% Overhead')
    plot._legend.set_title('System')
    #plot = data.groupby(['system']).plot(yerr={'time_mean_base': data['time_sem_base'], 'time_mean_ebph': data['time_sem_ebph']},
    #        y='overhead',
    #        x='time_mean_base',
    #        kind='scatter',
    #        capsize=2,
    #        )
    #plot.set_xlabel(r'Base Time ($\mu$s)')
    #plot.set_ylabel(r'Overhead')
    #plot.legend(['Base', 'ebpH'])
    plot.savefig(f'{prefix}.png', bbox_inches='tight', dpi=200)

base, ebph = parse_all_results('arch-3day/results')
arch = compare(base, ebph)
base, ebph = parse_all_results('homeostasis-3day/results')
homeostasis = compare(base, ebph)
base, ebph = parse_all_results('bronte-7day/results')
bronte = compare(base, ebph)

arch['system'] = 'arch'
homeostasis['system'] = 'homeostasis'
bronte['system'] = 'bronte'

data = pd.concat([arch, homeostasis, bronte])

export_data(data, 'all_overheads')
