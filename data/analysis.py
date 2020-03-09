#! /usr/bin/env python3

import os, sys
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('base', type=str)
parser.add_argument('ebph', type=str)
parser.add_argument('out_dir', type=str)
args = parser.parse_args(sys.argv[1:])

TOP_OVERHEAD_PATH = os.path.join(args.out_dir, 'overhead-by-overhead.tex')
TOP_COUNT_PATH = os.path.join(args.out_dir, 'overhead-by-count.tex')

def combine(base, ebph):
    base = base.rename(columns={'time':'t-base', 'count':'c-base'})
    ebph = ebph.rename(columns={'time':'t-ebph', 'count':'c-ebph'})
    data = pd.merge(base, ebph)
    data.loc[:, 'count'] = data[:]['c-base'] + data[:]['c-ebph']
    data.loc[:, 'time'] = data[:]['t-base'] + data[:]['t-ebph']
    data = data.sort_values(['count', 'time'], ascending=[0, 0])

    #data = data.drop(columns=['count', 'time'])
    #data = data.loc[:, ['syscall', 'c-base', 't-base', 'c-ebph', 't-ebph']]
    data = data.drop(columns=['c-base', 'c-ebph', 'time'])
    data = data.loc[:, ['syscall', 'count', 't-base', 't-ebph']]

    data.loc[:, 'overhead'] = (data[:]['t-ebph'] - data[:]['t-base']) / data[:]['t-base'] * 100

    return data

def top_overhead_table(data, top=20):
    data[:]['syscall'] =  data[:]['syscall'].str.replace('_', r'\_')

    # Sort then top
    data = data.sort_values(['overhead'], ascending=[0])
    data = data[:top]

    # Rename columns
    data = data.rename(columns={'syscall':'System Call', 't-base':r't-base($\mu$s/call)',
        't-ebph':r't-ebpH($\mu$s/call)', 'overhead':r'Overhead(\%)', 'count':'Count'})
    data.to_latex(index=0, escape=0, buf=TOP_OVERHEAD_PATH)

def top_count_table(data, top=20):
    data[:]['syscall'] =  data[:]['syscall'].str.replace('_', r'\_')

    # Top then sort
    data = data[:top]
    data = data.sort_values(['overhead'], ascending=[0])

    # Rename columns
    data = data.rename(columns={'syscall':'System Call', 't-base':r't-base($\mu$s/call)',
        't-ebph':r't-ebpH($\mu$s/call)', 'overhead':r'Overhead(\%)', 'count':'Count'})
    data.to_latex(index=0, escape=0, buf=TOP_COUNT_PATH)

base = pd.read_csv(args.base, sep=r'\s+', skiprows=5, error_bad_lines=0, names=['syscall', 'count', 'time'])
base = base.sort_values(['count', 'time'], ascending=[0, 0])

ebph = pd.read_csv(args.ebph, sep=r'\s+', skiprows=5, error_bad_lines=0, names=['syscall', 'count', 'time'])
ebph = ebph.sort_values(['count', 'time'], ascending=[0, 0])

top_overhead_table(combine(base, ebph))
top_count_table(combine(base, ebph))

#print(ebph[:20][['syscall', 'count', 'time']].to_latex(index=0))
#
#plot = ebph.plot(x='syscall', y='time', kind='bar')
