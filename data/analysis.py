#! /usr/bin/env python3

import os, sys
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--base', type=str, nargs='+', required=1, help='base data')
parser.add_argument('-e', '--ebph', type=str, nargs='+', required=1, help='ebpH data')
parser.add_argument('-o', '--out', type=str, help='Path to output table')
parser.add_argument('-f', '--figs', type=str, help='Output figs as ...-<figs>.png')
parser.add_argument('--noavg', action='store_true', help='Do not average times')
args = parser.parse_args(sys.argv[1:])

pd.options.display.float_format = '{:.2f}'.format
sns.set()

def read_benchmarks(*files):
    """
    Read benchmarking data from ss files and return a series of data frames.
    """
    data = []
    for f in files:
        data.append(pd.read_csv(f, sep=r'\s+', skiprows=5, error_bad_lines=0, names=['syscall', 'count', 'time']))
    return data

def merge_frames(*data):
    """
    Merge many frames together. Should not be called on "averaged" data.
    """
    result = pd.concat(*data).groupby(['syscall'], as_index=False)[["count", "time"]].sum()
    return result

def average_times(data):
    """
    Convert time to average time.
    """
    # Calculate average times
    data.loc[:, 'time'] = data.loc[:, 'time'] / data.loc[:, 'count']

def std_times(data):
    # Calculate standard deviations
    std = data['time'].std()
    mean = data['time'].mean()
    data['stdev'] = np.abs(data['time'] - mean) / std
    return data

def std_overhead(data):
    std = data['overhead'].std()
    mean = data['overhead'].mean()
    data['stdev_overhead'] = np.abs(data['overhead'] - mean) / std
    return data

def calculate(base, ebph):
    """
    Join tables and calculate values.
    """
    data = pd.merge(base, ebph, on=['syscall'], suffixes=('_base', '_ebph'))
    # Overhead
    data.loc[:, 'overhead'] = (data[:]['time_ebph'] - data[:]['time_base']) / data[:]['time_base'] * 100
    # Total count
    data.loc[:, 'total_count'] = data[:]['count_ebph'] + data[:]['count_base']
    # Percent of data points
    data.loc[:, 'percent_data'] = data[:]['total_count'] / sum(data[:]['total_count']) * 100
    return data

def strip_outliers(data):
    data = data[(data['stdev_base'] < 3) & (data['stdev_ebph'] < 3 & (data['stdev_overhead'] < 3))]
    #data = data[data['overhead'] > 0]
    return data

def sort_and_filter(data, top=20, sort='total_count'):
    # Sort and slice data
    data = data.sort_values(sort, ascending=0)
    data = data[:top]
    return data

def plot_times(data, suffix=''):
    data['key'] = data['time_base'] + data['time_ebph']
    data = data.sort_values('key')
    data = data[['syscall', 'time_base', 'time_ebph']]
    errors = data.sem()
    plot = data.plot(yerr={'time_base': errors['time_base'],'time_ebph': errors['time_ebph']},
            y=['time_base', 'time_ebph'],
            x='syscall',
            kind='bar',
            capsize=2)
    plot.set_xlabel("System Call")
    plot.set_ylabel("Time ($\mu$s)")
    plot.legend(['Base', 'ebpH'])
    plot.get_figure().savefig('times-' + suffix + '.png', bbox_inches='tight', dpi=200)

def plot_overheads(data, suffix=''):
    data = data.sort_values('overhead')
    data = data[['syscall', 'overhead']]
    errors = data.sem()
    plot = data.plot(yerr={'overhead': errors['overhead']},
            y='overhead',
            x='syscall',
            kind='bar',
            capsize=2)
    plot.set_xlabel("System Call")
    plot.set_ylabel("Overhead (%)")
    plot.legend().remove()
    plot.get_figure().savefig('overheads-' + suffix + '.png', bbox_inches='tight', dpi=200)

def export_table(data, path):
    """
    Export final table as LaTeX table.
    """
    # Keep columns we care about
    data['time_base'] = data['time_base'].map('{:.3f}'.format) + ' ' + data['stdev_base'].map('({:.4f})'.format)
    data['time_ebph'] = data['time_ebph'].map('{:.3f}'.format) + ' ' + data['stdev_ebph'].map('({:.4f})'.format)
    data['overhead'] = data['overhead'].map('{:.3f}'.format) + ' ' + data['stdev_overhead'].map('({:.4f})'.format)
    data = data[['syscall', 'time_base', 'time_ebph', 'overhead']]
    # Export table, after renaming columns
    if args.out:
        data[:]['syscall'] =  data[:]['syscall'].str.replace('_', r'\_')
        data = data.rename(columns={
            'syscall':r'\multicolumn{1}{l}{System Call}',
            'time_base':r'$T_{\text{base}}$ ($\mu$s)',
            'time_ebph':r'$T_{\text{ebpH}}$ ($\mu$s)',
            'overhead':r'\% Overhead'})
        data.to_latex(index=0, escape=0, buf=path, column_format=r'>{\ttfamily}lrrrr')
    else:
        print(data)

if __name__ == '__main__':
    base = merge_frames(read_benchmarks(*args.base))
    ebph = merge_frames(read_benchmarks(*args.ebph))

    if not args.noavg:
        average_times(base)
        average_times(ebph)

    base = std_times(base)
    ebph = std_times(ebph)

    data = calculate(base, ebph)
    data = std_overhead(data)
    data = strip_outliers(data)

    # Custom filtration
    #data = data[data['time_base'] < 7]

    data = sort_and_filter(data, top=20)

    if args.figs:
        plot_times(data, args.figs)
        plot_overheads(data, args.figs)

    export_table(data, args.out)

