import pandas as pd
import os, sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def plot_signals(df):
    # grid is 3x3 block, with each block 4x4

    fig = plt.figure(figsize=(10, 8))
    outer = gridspec.GridSpec(3, 3, wspace=0.2, hspace=0.2)

    for i in range(3*3):
        inner = gridspec.GridSpecFromSubplotSpec(4, 4,
                        subplot_spec=outer[i], wspace=0.1, hspace=0.1)

        grid_row = i // 3 + 1
        grid_col = i % 3 + 1
        for j in range(4*4):
            ax = plt.Subplot(fig, inner[j])
            block_row = (j//4) % 4 + 1
            block_col = j % 4 + 1
            row = df[(df.grid_row == grid_row) & (df.block_row == block_row)]
            value = row[f'Diff{(grid_col-1)*4+block_col}'].values[0]
            #print(grid_row, grid_col, block_row, block_col, value, (grid_col-1)*4+block_col)
            t = ax.text(0.5,0.5, f'{value:.2f}')
            #t = ax.text(0.5,0.5, f'{grid_row},{grid_col},{block_row},{block_col}')

            t.set_ha('center')
            ax.set_xticks([])
            ax.set_yticks([])
            fig.add_subplot(ax)

    #fig.show()
    plt.show()
    #pass


def process_sheet(k, df_in):
    # format is 3x3 grid of Bottom/Top/Bottom/Top/Bottom/Top/Bottom/Top (4x4 peaks)
    # first locate each of the 9 4x4 blocks, getting a grid row and column
    # then, for each 4x4, get row,column values and bottom & top values
    # Columns should be something like:
    #   Experiment, Date, grid_row, grid_col, block_row, bottom1, top1, bottom2, top2, bottom3, top3, bottom4, top4
    #   But then convert the bottom/topX to just a bottom/top cols with a block_col column.
    # Should be 4 rows for each of the 4 block rows.

    # start by giving names to columns for ease of selection
    date = str(df_in.columns[0]).split(' ')[0]  # save this date, stripping off time.
    experiment = k
    column_mapping = {
        df_in.columns[0]: 'Experiment', # useful
        'Unnamed: 10': 'block_row',  # useful but hardcoded
    }

    num_grid_rows = 3
    num_blocks = 4
    for (cstart_idx, bstart_idx) in [(1,1), (11,5), (21,9)]:  # 3 grid items across
        column_mapping.update({f'Unnamed: {i+cstart_idx}': f'Bottom{j+bstart_idx}' for i,j in zip(range(0, num_blocks*2, 2), range(0,num_blocks))})
        column_mapping.update({f'Unnamed: {i+cstart_idx}': f'Top{j+bstart_idx}' for i,j in zip(range(1, num_blocks*2+1, 2), range(0,num_blocks))})

    #print(column_mapping)

    df = df_in.rename(columns = column_mapping)  # rename and copy

    df['Date'] = date
    df['Experiment'] = experiment
    df['block_row'] = df.block_row.astype(int, errors='ignore')
    df['grid_row'] = 0 #[1]*4 + [2]*4 + [3]*4

    cols_to_use = ['Experiment', 'Date', 'grid_row', 'block_row'] + [f'Bottom{x}' for x in range(1,13)] + [f'Top{x}' for x in range(1,13)]
    df = df[cols_to_use]
    df = df[~(pd.isnull(df.block_row))].reset_index() # | ~(pd.isnull(df.Bottom1))]
    df['grid_row'] = [1]*4 + [2]*4 + [3]*4

    # might as well get top-bottom columns
    for num in range(1, 13):
        df[f'Bottom{num}'] = pd.to_numeric(df[f'Bottom{num}'], errors='coerce')
        df[f'Top{num}'] = pd.to_numeric(df[f'Top{num}'], errors='coerce')
        df[f'Diff{num}'] = df[f'Top{num}'] - df[f'Bottom{num}']

    # reorder columns
    all_cols = set(df.columns)
    ordered_cols = [[f'Bottom{n}', f'Top{n}', f'Diff{n}'] for n in range(1, 13)]
    ordered_cols = sum(ordered_cols, [])

    other_cols = ['Experiment', 'Date', 'grid_row', 'block_row']
    other_cols += (all_cols - set(other_cols) - set(ordered_cols))
    df = df[other_cols + ordered_cols] #.reset_index(drop=True)

    # now have all data in a better format but really just want a bottom and top row, not e.g. Bottom4
    #print(df)
    #for num in range(1, 13):
    #    print(df[f'Bottom{num}'].T)

    # might possibly also want to add diff columns to the original spreadsheet df_in

    # finally, might want to plot the signals in a grid that matches the original layout.
    plot_signals(df)

    return df


parser = argparse.ArgumentParser()
parser.add_argument('--inputFiles', '-inputFiles', dest='inputFiles', nargs='*', help='inputFiles list of input files')
parser.add_argument('--outputFile', '-outputFile', dest='outputFile', nargs='?', default=None   , help='outputFile output file name (if none, use stdout)')
args = parser.parse_args()

converted_sheets = {}

for index, fname in enumerate(args.inputFiles):
    dict_sheets = pd.read_excel(fname, sheet_name=None)
    #print(dict_sheets.keys())
    for k, v in dict_sheets.items():
        if 'Blank' in k:
            continue
        converted_sheets[k] = process_sheet(k, v)

    df = pd.concat(converted_sheets.values()).drop('index', axis=1)
    print(df)
    if args.outputFile is None:
        dirname = os.path.dirname(fname)
        basename = os.path.basename(fname)
        outputFile = os.path.join(dirname, 'converted_' + basename)
    else:
        dirname = os.path.dirname(args.outputFile)
        basename = os.path.basename(args.outputFile)
        outputFile = os.path.join(dirname, f'{index}_' + basename)
    df.to_excel(outputFile, index=False)
