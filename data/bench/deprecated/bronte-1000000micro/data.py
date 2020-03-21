#! /usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

base = []
base.append(pd.read_csv('./base/null.log', sep=r'\s+', error_bad_lines=0, names=['count', 'time']))
base.append(pd.read_csv('./base/simple.log', sep=r'\s+', error_bad_lines=0, names=['count', 'time']))
base.append(pd.read_csv('./base/system.log', sep=r'\s+', error_bad_lines=0, names=['count', 'time']))

base = pd.concat(base, ignore_index=True)
base['test'] = ['clone', 'clone/exec', 'system']
base['time'] = base['time'] / base['count']
base = base[['test', 'count', 'time']]

ebph = []
ebph.append(pd.read_csv('./ebph/null.log', sep=r'\s+', error_bad_lines=0, names=['count', 'time']))
ebph.append(pd.read_csv('./ebph/simple.log', sep=r'\s+', error_bad_lines=0, names=['count', 'time']))
ebph.append(pd.read_csv('./ebph/system.log', sep=r'\s+', error_bad_lines=0, names=['count', 'time']))

ebph = pd.concat(ebph, ignore_index=True)
ebph['test'] = ['clone', 'clone/exec', 'system']
ebph['time'] = ebph['time'] / ebph['count']
ebph = ebph[['test', 'count', 'time']]

data = pd.merge(base, ebph, on=['test', 'count'], suffixes=['_base', '_ebph'])
data['overhead'] = (data['time_ebph'] - data['time_base']) / data['time_base'] * 100
errors = data.agg(['mean', 'std'])
for ix in ['time_base', 'time_ebph', 'overhead']:
    deviations = np.abs(data[ix] - errors[ix]['mean']) / errors[ix]['std']
    data[ix] = data[ix].map('{:.3f}'.format) + deviations.map(' ({:.4f})'.format)

data = data.rename(columns={
    'test':r'\multicolumn{1}{l}{Test}',
    'count':r'Count',
    'time_base':r'$T_{\text{base}}$ ($\mu$s)',
    'time_ebph':r'$T_{\text{ebpH}}$ ($\mu$s)',
    'overhead':r'\% Overhead'})
data.to_latex(index=0, escape=0, buf='results.tex', column_format=r'>{\ttfamily}lrrrr')
