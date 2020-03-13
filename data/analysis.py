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
parser.add_argument('--noavg', action='store_true', help='Do not average times')
args = parser.parse_args(sys.argv[1:])

pd.options.display.float_format = '{:.2f}'.format

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
    data.loc[:, 'time'] = data.loc[:, 'time'] / data.loc[:, 'count']

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
    # FIXME: change this
    data = data[data['time_base'] < 7]
    data = data[np.abs(data['overhead'] - data['overhead'].mean() <= (3 * data['overhead'].std()))]
    return data

def sort_and_filter(data, top=20, sort='total_count'):
    # Sort and slice data
    data = data.sort_values(sort, ascending=0)
    data = data[:top]
    return data

def export_table(data, path):
    """
    Export final table as LaTeX table.
    """
    # Keep columns we care about
    data = data[['syscall', 'time_base', 'time_ebph', 'overhead']]
    # Export table, after renaming columns
    data[:]['syscall'] =  data[:]['syscall'].str.replace('_', r'\_')
    data = data.rename(columns={
        'syscall':r'\multicolumn{1}{l}{System Call}',
        'time_base':r'$T_{\text{base}}$ ($\mu$s)',
        'time_ebph':r'$T_{\text{ebpH}}$ ($\mu$s)',
        'overhead':r'\% Overhead'})
    data.to_latex(index=0, escape=0, buf=path, column_format=r'>{\ttfamily}lrrrr')

if __name__ == '__main__':
    base = merge_frames(read_benchmarks(*args.base))
    if not args.noavg:
        average_times(base)

    ebph = merge_frames(read_benchmarks(*args.ebph))
    if not args.noavg:
        average_times(ebph)

    data = calculate(base, ebph)
    data = strip_outliers(data)
    data = sort_and_filter(data)
    print(data)
    if args.out:
        export_table(data, args.out)

