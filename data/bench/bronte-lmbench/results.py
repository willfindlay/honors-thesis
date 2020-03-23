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

KEYS = {
        'signal': 'type',
        'ipc': 'type',
        'select': ['type', 'count'],
        'syscall': 'syscall',
        'process': 'process',
        }

def parse_syscall_results(f):
    data = []
    with open(f, 'r') as f:
        for line in f.readlines():
            match = re.match(r'Simple\s+([^:]+):\s(\d+\.\d+).*', line)
            if not match:
                continue
            data.append((match[1], np.float(match[2])))
    data = pd.DataFrame(data, columns=['syscall', 'time'])
    data.loc[data['syscall'] == 'syscall', 'syscall'] = 'getppid'
    return data

def parse_process_results(f):
    data = []
    with open(f, 'r') as f:
        for line in f.readlines():
            match = re.match(r'Process\s+([^:]+):\s(\d+\.\d+).*', line)
            if not match:
                continue
            data.append((match[1], np.float(match[2])))
    data = pd.DataFrame(data, columns=['process', 'time'])
    return data

def parse_select_results(f):
    data = []
    with open(f, 'r') as f:
        for line in f.readlines():
            match = re.match(r'Select on (\d+) (.*)\s*fd\'s: (\d+\.\d+).*', line)
            if not match:
                continue
            data.append(('TCP Socket' if 'tcp' in match[2] else 'Regular File', match[1], np.float(match[3])))
    data = pd.DataFrame(data, columns=['type', 'count', 'time'])
    return data

def parse_signal_results(f):
    data = []
    with open(f, 'r') as f:
        for line in f.readlines():
            match = re.match(r'Signal handler ([^:]+): (\d+\.\d+).*', line)
            if not match:
                continue
            data.append((match[1], np.float(match[2])))
    data = pd.DataFrame(data, columns=['type', 'time'])
    data.loc[data['type'] == 'installation', 'type'] = 'Installation'
    data.loc[data['type'] == 'overhead', 'type'] = 'Handler'
    return data

def parse_ipc_results(f):
    data = []
    with open(f, 'r') as f:
        for line in f.readlines():
            match = re.match(r'(AF_UNIX|Pipe)[^:]*latency: (\d+\.\d+).*', line)
            if not match:
                continue
            data.append((match[1], np.float(match[2])))
    data = pd.DataFrame(data, columns=['type', 'time'])
    return data

def parse_results_file(f):
    if 'base' in f:
        ftype = 'base'
    elif 'ebph' in f:
        ftype = 'ebph'
    else:
        raise Exception(f'{f} does not contain "base" or "ebph"')
    dfs = {}
    dfs['syscall'] = parse_syscall_results(f)
    dfs['process'] = parse_process_results(f)
    dfs['select'] = parse_select_results(f)
    dfs['signal'] = parse_signal_results(f)
    dfs['ipc'] = parse_ipc_results(f)
    return (ftype, dfs)

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
    keyed_data = {}
    for k in data[0].keys():
        keyed_data[k] = [d[k] for d in data]
    for k in keyed_data.keys():
        combined = pd.concat(keyed_data[k])
        combined = combined.groupby(KEYS[k], as_index=False).agg({'time': [ 'mean', 'std', 'sem']})
        combined.columns = ['_'.join(col).strip('_') for col in combined.columns.values]
        keyed_data[k] = combined
    return keyed_data

def compare(k, base, ebph):
    base = base[k]
    ebph = ebph[k]
    data = pd.merge(base, ebph, on=KEYS[k], suffixes=['_base', '_ebph'])
    data['diff'] = (data['time_mean_ebph'] - data['time_mean_base'])
    data['overhead'] = data['diff'] / data['time_mean_base'] * 100
    return data

def compare_all(base, ebph):
    compared = {}
    for k in base.keys():
        compared[k] = compare(k, base, ebph)
    return compared

def export_all(data):
    for k in data.keys():
        export_data(data[k], k)

def export_data(data, prefix):
    # Make table
    table_data = data.copy()
    if prefix != 'select':
        table_data = table_data.sort_values('time_mean_base', ascending=1)
    table_data['time_base'] = table_data['time_mean_base'].map('{:.3f} '.format) + \
            table_data['time_std_base'].map('({:.4f})'.format)
    table_data['time_ebph'] = table_data['time_mean_ebph'].map('{:.3f} '.format) + \
            table_data['time_std_ebph'].map('({:.4f})'.format)
    if prefix == 'signal':
        column_format = r'>{\ttfamily}lrrrr'
        table_data = table_data[['type', 'time_base', 'time_ebph', 'diff', 'overhead']]
    if prefix == 'ipc':
        column_format = r'>{\ttfamily}lrrrr'
        table_data = table_data[['type', 'time_base', 'time_ebph', 'diff', 'overhead']]
        table_data['type'] = table_data['type'].str.replace('_', r'\_')
    if prefix == 'select':
        table_data = table_data.sort_values(['type', 'count'], ascending=[1, 1])
        column_format = r'>{\ttfamily}llrrrr'
        table_data = table_data[['type', 'count', 'time_base', 'time_ebph', 'diff', 'overhead']]
    if prefix == 'syscall':
        column_format = r'>{\ttfamily}lrrrr'
        table_data = table_data[['syscall', 'time_base', 'time_ebph', 'diff', 'overhead']]
    if prefix == 'process':
        column_format = r'>{\ttfamily}lrrrr'
        table_data = table_data[['process', 'time_base', 'time_ebph', 'diff', 'overhead']]
    table_data = table_data.rename(columns={
        'count': r'Count',
        'type': r'\multicolumn{1}{l}{Type}',
        'syscall': r'\multicolumn{1}{l}{System Call}',
        'process': r'\multicolumn{1}{l}{Process}',
        'time_base': r'$T_\text{base}$ ($\mu$s)',
        'time_ebph': r'$T_\text{ebpH}$ ($\mu$s)',
        'diff':r'Diff. ($\mu$s)',
        'overhead':r'\% Overhead',
        })
    table_data.to_latex(index=0, escape=0, buf=f'{prefix}_results.tex', column_format=column_format)
    # Make figure
    figure_data = data.copy()
    figure_data = figure_data.sort_values('time_mean_base', ascending=1)
    if prefix == 'signal':
        x = 'type'
        xlab = "Signal Event"
    if prefix == 'ipc':
        x = 'type'
        xlab = "Kind"
    if prefix == 'select':
        figure_data = figure_data.sort_values(['type', 'count'], ascending=[1, 1])
        figure_data['key'] = figure_data['type'] + figure_data['count'].map(' ({})'.format)
        x = 'key'
        xlab = "Type (Count)"
    if prefix == 'syscall':
        x = 'syscall'
        xlab = "System Call"
    if prefix == 'process':
        x = 'process'
        xlab = "Process"
    plot = figure_data.plot(yerr={'time_mean_base': figure_data['time_sem_base'], 'time_mean_ebph': figure_data['time_sem_ebph']},
            y=['time_mean_base', 'time_mean_ebph'],
            x=x,
            kind='bar',
            capsize=2,
            )
    plot.set_xlabel(xlab)
    plot.set_ylabel(r"Time ($\mu$s)")
    plot.legend(['Base', 'ebpH'])
    plot.get_figure().savefig(f'{prefix}_times.png', bbox_inches='tight', dpi=200)

base, ebph = parse_all_results('full')
data = compare_all(base, ebph)
export_all(data)
