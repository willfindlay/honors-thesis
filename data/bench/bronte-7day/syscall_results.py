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

pd.options.display.float_format = '{:.4f}'.format

def parse_bpfbench_data(csv):
    data = pd.read_csv(csv, sep=r'\s+', skiprows=5, header=0)
    data.columns = ['syscall', 'count', 'time']
    # Uncomment if we need to average (newer versions of the script)
    #data['time'] = data['time'] / data['count']
    return data

def operate(base, ebph):
    data = base.merge(ebph, on=['syscall'], suffixes=['_base', '_ebph'])
    data['increase'] = (data['time_ebph'] - data['time_base'])
    data['overhead'] = (data['time_ebph'] - data['time_base']) / data['time_base'] * 100
    data = data.sort_values(['time_base'], ascending=[1])
    return data

def discard_outliers(data):
    data = data[(np.abs(sp.stats.zscore(data['time_base'])) < 3)]
    data = data[(np.abs(sp.stats.zscore(data['time_ebph'])) < 3)]
    data = data[(np.abs(sp.stats.zscore(data['overhead'])) < 3)]
    data = data[(np.abs(sp.stats.zscore(data['increase'])) < 3)]
    return data

def bpfbench_to_tex(data, prefix):
    data = data.copy()
    # Format values
    data['increase'] = data['increase'].map('{:.3f}'.format)
    data['overhead'] = data['overhead'].map('{:.2f}'.format)
    data['time_base'] = data['time_base'].map('{:.3f}'.format)
    data['time_ebph'] = data['time_ebph'].map('{:.3f}'.format)
    data['syscall'] = data['syscall'].str.replace('_', r'\_')
    # Select columns
    data = data[['syscall', 'time_base', 'time_ebph', 'increase', 'overhead']]
    # Rename columns
    data = data.rename(columns={
        'syscall': r'\multicolumn{1}{l}{System Call}',
        'time_base': r'$T_\text{base}$ ($\mu$s)',
        'time_ebph': r'$T_\text{ebpH}$ ($\mu$s)',
        'increase':r'Diff. ($\mu$s)',
        'overhead':r'\% Overhead',
        })
    # Export
    data.to_latex(index=0, escape=0, buf=f'{prefix}.tex', column_format=r'>{\ttfamily}lrrrr')

def bpfbench_to_time_graphs(data, prefix, figsize=(8, 6)):
    data = data.copy()
    data = data.sort_values('time_base')
    stderr = data.sem().to_dict()
    plot = data.plot(
            yerr=stderr,
            y=['time_base', 'time_ebph'],
            x='syscall',
            kind='bar',
            capsize=2,
            figsize=figsize,
            )
    plot.set_xlabel("System Call")
    plot.set_ylabel(r"Time ($\mu$s)")
    plot.legend(['Base', 'ebpH'])
    plot.get_figure().savefig(f'{prefix}.png', type='png', bbox_inches='tight', dpi=200)

def ttest_times(data):
    base = data['time_base']
    ebph = data['time_ebph']

    alpha = 0.05
    ttest = sp.stats.ttest_ind(base, ebph)
    print(ttest)

    if ttest.pvalue / 2 < alpha and ttest.statistic > 0:
        print('reject H0 base > ebpH')
    else:
        print('accept H0 base > ebpH')

# Parse data
base = parse_bpfbench_data('base.log')
ebph = parse_bpfbench_data('ebph.log')

# Combine data
data = operate(base, ebph)
data = discard_outliers(data)

# Output starts here
under_3us = data.copy()
under_3us = under_3us[under_3us['time_base'] < 3]
under_3us = under_3us.sort_values('count_base')[:20]
bpfbench_to_tex(under_3us, 'under_3us_times')
bpfbench_to_time_graphs(under_3us, 'under_3us_times')

lmbench_parity = data.copy()
lmbench_parity = lmbench_parity[data['syscall'].isin(['getppid', 'write', 'read', 'fstat', 'stat', 'open', 'close'])]
bpfbench_to_tex(lmbench_parity, 'lmbench_parity_times')
bpfbench_to_time_graphs(lmbench_parity, 'lmbench_parity_times')

#top_20 = data.copy()
#top_20 = top_20.sort_values('count_base')[:20]
#bpfbench_to_tex(top_20, 'top_20')
#bpfbench_to_time_graphs(top_20, 'top_20', (8, 11))

ttest_times(data)
