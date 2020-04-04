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

from results import parse_all_results

def combine_data(data):
    combined = pd.concat(data)
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
    return data

def export_data(orig, prefix):
    # Make table --------------------------------------------------------
    data = orig.copy()

    # Sort by count
    data = data.sort_values('count', ascending=0)

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
    data.to_latex(index=0, escape=0, buf=f'{prefix}_full_results.tex', column_format=column_format,
            longtable=True,
            caption=f'All system call overhead data from the \\code{{{prefix.replace("_", "-")}}} dataset.',
            label=f'tab:{prefix}_full')

base, ebph = parse_all_results('results')
data = compare(base, ebph)
export_data(data, 'homeostasis_3day')
