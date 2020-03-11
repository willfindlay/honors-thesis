import pandas as pd

data = pd.DataFrame()

data.insert(0, 'System', ['arch', 'bronte', 'homeostasis'])
data.insert(1, 'Description', ['Personal workstation', 'CCSL workstation', 'Mediawiki server for COMP3000 class wiki'])

with pd.option_context("max_colwidth", 1000):
    data = data.rename(columns={
        'System': r'\multicolumn{1}{l}{System}'
        })
    print(data.to_latex(index=0, escape=0, column_format=r'>{\ttfamily}ll'))

data = pd.DataFrame(columns=['System', 'Dataset', 'Workload', 'Description'])
data.loc[len(data)] = ['arch', 'arch-3day', 'Normal use', 'Macrobenchmark using bpfbench, 3 days with ebpH and 3 days without']
data.loc[len(data)] = ['homeostasis', 'homeostasis-7day', 'Production', 'Macrobenchmark using bpfbench, 7 days with ebpH and 7 days without']
data.loc[len(data)] = ['bronte', 'arch-7day', 'Idle', 'Macrobenchmark using bpfbench, 7 days with ebpH and 7 days without']
data.loc[len(data)] = ['arch', 'arch-close', 'Artificial', 'Microbenchmark using bpfbench, running 1,000,000 close(2) system calls with invalid arguments.']

data = data.sort_values(by=['System', 'Dataset'])

with pd.option_context("max_colwidth", 1000):
    data = data.reindex(columns=['Dataset', 'System', 'Workload', 'Description'])
    data = data.rename(columns={
        'Dataset': r'\multicolumn{1}{l}{Dataset}',
        'System': r'\multicolumn{1}{l}{System}'
        })
    print(data.to_latex(index=0, escape=0, column_format=r'>{\ttfamily}l>{\ttfamily}llp{2.3in}'))
