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

def parse_lmbench_data(csv):
    data = []
    with open(csv) as f:
        for line in f:
            match = re.match(r'Simple\s+([^:]+): (\d+\.\d*)', line)
            if not match:
                continue
            data.append((match[1], np.float(match[2])))
    data = pd.DataFrame(data, columns=['syscall', 'time'])
    data.loc[data['syscall'] == 'syscall', 'syscall'] = 'getppid'
    data = data.groupby('syscall', as_index=False).agg({'time': [ 'mean', 'std', 'sem']})
    return data

def operate(base, ebph):
    data = base.merge(ebph, on=['syscall'], suffixes=['_base', '_ebph'])
    data['overhead'] = (data['time_ebph', 'mean'] - data['time_base', 'mean']) / data['time_base', 'mean'] * 100
    data['increase'] = (data['time_ebph', 'mean'] - data['time_base', 'mean'])
    data = data.sort_values([('time_base', 'mean')], ascending=[1])
    return data

def lmbench_to_tex(data, buf):
    new_time_base = data['time_base', 'mean'].map('{:.3f} '.format) + data['time_base', 'std'].map('({:.4f})'.format)
    new_time_ebph = data['time_ebph', 'mean'].map('{:.3f} '.format) + data['time_ebph', 'std'].map('({:.4f})'.format)
    data['increase'] = data['increase'].map('{:.3f}'.format)
    data['overhead'] = data['overhead'].map('{:.2f}'.format)
    data = data.drop(columns=['time_base', 'time_ebph'])
    data['time_base'] = new_time_base
    data['time_ebph'] = new_time_ebph
    data = data[['syscall', 'time_base', 'time_ebph', 'increase', 'overhead']]
    data['syscall'] =  data['syscall'].str.replace('_', r'\_')
    data = data.rename(columns={
        'syscall': r'\multicolumn{1}{l}{System Call}',
        'time_base': r'$T_\text{base}$ ($\mu$s)',
        'time_ebph': r'$T_\text{ebpH}$ ($\mu$s)',
        'increase':r'Diff. ($\mu$s)',
        'overhead':r'\% Overhead',
        })
    # Get rid of that stupid \\
    latex = data.to_latex(index=0, escape=0, column_format=r'>{\ttfamily}lrrrr')
    latex = latex.split('\n')
    latex = latex[:3] + latex[4:]
    latex = '\n'.join(latex)
    with open(buf, 'w') as f:
        f.write(latex)

def lmbench_to_figs(data):
    data.columns = ['_'.join(col).strip() for col in data.columns.values]
    data.columns = [col.strip('_') for col in data.columns.values]
    data = data.reset_index()

    plot = data.plot(yerr={'time_base_mean': data['time_base_std'], 'time_ebph_mean': data['time_ebph_std']},
            y=['time_base_mean', 'time_ebph_mean'],
            x='syscall',
            kind='bar',
            capsize=4)
    plot.set_xlabel("System Call")
    plot.set_ylabel(r"Time ($\mu$s)")
    plot.legend(['Base', 'ebpH'])
    plot.get_figure().savefig('syscall_times.png', bbox_inches='tight', dpi=200)

base = parse_lmbench_data('./results/base-1000.log')
ebph = parse_lmbench_data('./results/ebph-1000.log')
data = operate(base, ebph)
print(lmbench_to_tex(data, 'syscall_results.tex'))
lmbench_to_figs(data)

