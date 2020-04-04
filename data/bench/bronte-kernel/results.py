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

def parse_category_results(f):
    data = []
    data = pd.read_csv(f, sep=r'\s+')
    data = data.T
    data = data.stack()
    data = data.reset_index(level=0)
    data['level_0'] = data['level_0'].map(lambda s: s[0].upper() + s[1:].lower())
    data.columns = ['category', 'time']
    return data

def parse_results_file(f):
    if 'base' in f:
        ftype = 'base'
    elif 'ebph' in f:
        ftype = 'ebph'
    else:
        raise Exception(f'{f} does not contain "base" or "ebph"')
    data = parse_category_results(f)
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
    combined = combined.groupby('category', as_index=False).agg({'time': [ 'mean', 'std', 'sem']})
    combined.columns = ['_'.join(col).strip('_') for col in combined.columns.values]
    return combined

def compare(base, ebph):
    data = pd.merge(base, ebph, on='category', suffixes=['_base', '_ebph'])
    data['diff'] = (data['time_mean_ebph'] - data['time_mean_base'])
    data['overhead'] = data['diff'] / data['time_mean_base'] * 100
    return data

def export_all(data):
    export_data(data, 'bronte_kernel')

def export_data(orig, prefix):
    # Make table --------------------------------------------------------
    data = orig.copy()

    data = data.reindex([1, 2, 0])

    # Format table
    column_format = r'>{\ttfamily}lrrrr'
    data['time_base'] = data['time_mean_base'].map('{:.3f} '.format) + \
            data['time_std_base'].map('({:.4f})'.format)
    data['time_ebph'] = data['time_mean_ebph'].map('{:.3f} '.format) + \
            data['time_std_ebph'].map('({:.4f})'.format)
    data = data[['category', 'time_base', 'time_ebph', 'diff', 'overhead']]
    data['category'] = data['category'].str.replace('_', r'\_')
    data = data.rename(columns={
        'category': r'\multicolumn{1}{l}{Category}',
        'time_base': r'$T_\text{base}$ (s)',
        'time_ebph': r'$T_\text{ebpH}$ (s)',
        'diff':r'Diff. (s)',
        'overhead':r'\% Overhead',
        })
    data.to_latex(index=0, escape=0, buf=f'{prefix}_results.tex', column_format=column_format)

    # Make figure -------------------------------------------------------
    #data = orig.copy()

    ## Get top 20 by count
    #data = data.sort_values('count', ascending=0)
    #data = data[:20]

    ## Plot
    #plot = data.plot(yerr={'time_mean_base': data['time_sem_base'], 'time_mean_ebph': data['time_sem_ebph']},
    #        y=['time_mean_base', 'time_mean_ebph'],
    #        x='category',
    #        kind='bar',
    #        capsize=2,
    #        logy=True,
    #        )
    #plot.set_xlabel('System Call')
    #plot.set_ylabel(r"Time ($\mu$s)")
    #plot.legend(['Base', 'ebpH'])
    #plot.get_figure().savefig(f'{prefix}_times.png', bbox_inches='tight', dpi=200)

base, ebph = parse_all_results('results')
data = compare(base, ebph)
export_all(data)
