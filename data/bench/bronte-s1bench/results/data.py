#! /usr/bin/env python3

import os, sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

TO_USEC = 1000000

def parse_s1bench_data(csv):
    data = (pd.read_csv(csv, sep=r'\s+', error_bad_lines=0, header=None))
    data = data.iloc[1:, 1:]
    data['type'] = ['spin', 'populate', 'run', 'rates']
    rates = data[data['type'] ==  'rates']
    rates = rates.iloc[:, :3].transpose()
    rates.columns = ['rate']
    data = data[data['type'] != 'rates']
    data = data.join(rates)
    data = data.drop([5], axis=1)
    data.columns = ['count', 'time', 'time_user', 'time_sys', 'type', 'rates']
    t = data['type']
    data = data.drop(['type'], axis=1)
    data.insert(0, 'type', t)
    #data['time'] = data['time'] * TO_USEC
    #data['rates'] = data['rates'] / TO_USEC
    return data

def s1bench_to_tex(data, buf=None):
    data = data.drop(['time_sys', 'time_user'], axis=1)
    types = data['type', 'ebph']
    data = data.drop(columns=['type'])
    data.insert(0, 'type', types)
    data = data.reindex(['type', 'count', 'time', 'rates'], axis=1, level=0)
    data = data[data['type'] != 'spin']
    data = data.rename(columns={
        'base': r'Base',
        'ebph': r'ebpH',
        'type':r'\multicolumn{1}{l}{Operation}',
        'count':r'Count',
        'time':r'Time (s)',
        'rates':r'Rates (events/s)'})
    return data.to_latex(index=0, escape=0, buf=buf, column_format=r'>{\ttfamily}lllllll')


base = parse_s1bench_data('./base.log')
ebph = parse_s1bench_data('./ebph.log')

data = pd.concat([base, ebph], keys=['base', 'ebph'], axis=1).swaplevel(axis=1).sort_index(axis=1, level=0)

s1bench_to_tex(data, buf='results-nobpfbench.tex')

#print(s1bench_to_tex(base))
#print(s1bench_to_tex(ebph))

#data = pd.merge(base, ebph, on=['test', 'count'], suffixes=['_base', '_ebph'])
#data['overhead'] = (data['time_ebph'] - data['time_base']) / data['time_base'] * 100
#errors = data.agg(['mean', 'std'])
#for ix in ['time_base', 'time_ebph', 'overhead']:
#    deviations = np.abs(data[ix] - errors[ix]['mean']) / errors[ix]['std']
#    data[ix] = data[ix].map('{:.3f}'.format) + deviations.map(' ({:.4f})'.format)
