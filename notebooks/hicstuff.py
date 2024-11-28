# First, we will make a function to read the `.log` file into a `pandas` df. 
import glob
import pandas as pd
import numpy as np
import os.path as op
from IPython.display import display

# All the files can be assigned to a list with glob.glob:
# logs = glob.glob("../results/SRR*/*.log")
# they can be read with a for loop, but it's too messy to show. 

# The .log file is a tab-separated file with 4 tables, so we have to make our own function to read it
# I wrapped it in a class to save all tables from each log in a single variable. 
class HiCQCLog(): 
    def __init__(self, logfile):
        reader = pd.read_csv(logfile, sep="\t", header=None, iterator=True)
        t1 = reader.get_chunk(4).dropna(axis=1)
        t1.columns=t1.iloc[0]
        self.t1 = t1.drop(0).reset_index()

        t2 = reader.get_chunk(6).dropna(axis=1)
        t2.columns=t2.iloc[0]
        self.t2 = t2.drop(4).reset_index()

        t3 = reader.get_chunk(7) .dropna(axis=1)
        t3.columns=t3.iloc[0]
        self.t3 = t3.drop(10).reset_index()

        t4 = reader.get_chunk(7).dropna(axis=1)
        t4.columns=t4.iloc[0]
        self.t4 = t4.drop(17).reset_index()
        
    def view(self):
        display(self.t1, self.t2, self.t3, self.t4)

# Make a function to plot .pngs with matplotlib

import os
import glob
import matplotlib.pyplot as plt
from PIL import Image

def plot_pngs_in_grid(image_folder, suffix=".png", ncol=3):
    """
    Plots all PNG images from a specified folder in a grid.
    
    Parameters:
    image_folder (str): Path to the folder containing the PNG files.
    num_cols (int): Number of columns in the grid layout. Default is 3.
    
    Returns:
    None
    """
    # Find all .png files in the folder
    # with a specified suffix (default: .png)
    #print(f"Plotting all images in '{os.path.join(image_folder, f'*{suffix}')}'")
    image_files = glob.glob(os.path.join(image_folder, f'*{suffix}'))

    # If no images found, print a message and return
    if not image_files:
        print(f"No PNG files found in {image_folder}.")
        return
    
    # Calculate the number of rows needed
    num_cols = ncol
    num_images = len(image_files)
    num_rows = (num_images + num_cols - 1) // num_cols  # Ceiling division

    # Create a matplotlib figure
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))

    # Flatten axes in case the grid is not a perfect rectangle
    axes = axes.flatten()

    # Loop through image files and plot them
    for i, image_file in enumerate(image_files):
        img = Image.open(image_file)  # Open the image file
        axes[i].imshow(img)
        axes[i].axis('off')  # Turn off axis labels
        axes[i].set_title(os.path.basename(image_file))  # Set image title (filename)

    # Hide any remaining empty subplots if the number of images is not a perfect fit for the grid
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    # Adjust layout to fit images and titles nicely
    plt.tight_layout()
    #plt.show()


def extract_a_coordinates(e1, name, restriction = 'full', chrom='chrX', smooth = False, res = None, csv = None, output_dir='../results', force = False):
    """
    Calculates the A-compartment intervals based on the sign of an E1 eigenvector
    and saves the intervals to a CSV file.

    Parameters:
        e1 (output from `cooler eigs_cis`): Eigenvector values where the sign determines compartment type.
        name (str): Identifier for the dataset (used in the output filename).
        chrom (str): Chromosome name (default: 'chrX').
        res (int): Resolution of the bins in base pairs .
        output_dir (str): Directory where the output CSV will be saved (default: '../results').

    Output file:
        A CSV file containing the A-compartment intervals with columns: chrom, start, end.
    Returns:
        pd.DataFrame: DataFrame containing A-compartment intervals. 
        (chrom, bin_start, bin_end, start, end, length)
    """
    # Handle NaN values by forward-filling up to 2 bins in gaps
    e1 = pd.Series(e1)  # Ensure e1 is a pandas Series
    if smooth:
        # Smooth the eigenvector values using a rolling window
        e1_filled = e1.rolling(5,1, center=True).sum()
    else:
        # Forward-fill NaN values up to 2 bins in gaps
        e1_filled = e1.ffill(limit=2, limit_area='inside')



    # Detect changes in the sign of the eigenvector
    sign_change_coords = np.where(np.diff((e1_filled > 0).astype(int)))[0]

    # Determine start and end bins for A compartments
    a_start_bin = sign_change_coords[e1_filled.iloc[sign_change_coords + 1] > 0] + 1
    a_end_bin = sign_change_coords[e1_filled.iloc[sign_change_coords] > 0] + 1

    print(f"Calculating A-compartment intervals for {name}")
    #print(f"Initial counts: {len(a_start_bin)} starts, {len(a_end_bin)} ends")

    # Handle edge case: if the last bin is part of an A compartment
    if e1_filled.iloc[-1] > 0:
        #print("Last bin is part of an A-compartment, appending end bin.")
        a_end_bin = np.append(a_end_bin, len(e1_filled) - 1)

    #print(f"Final counts: {len(a_start_bin)} starts, {len(a_end_bin)} ends")

    # Create a DataFrame for the A-compartment intervals
    df = pd.DataFrame({
        'chrom': [chrom] * len(a_start_bin),
        'bin_start': a_start_bin,
        'bin_end': a_end_bin,
        'start': a_start_bin * res,
        'end': a_end_bin * res,
        'length': (a_end_bin - a_start_bin) * res,
        'resolution': res
    })
    csv_columns = ['chrom', 'start', 'end', 'resolution']
    # Save the results to a CSV file
    if not csv:
        print("`csv`= None. Returning DataFrame only.")
        return df
    csv_name = op.join(output_dir,f'{name}_a_comp_coords_{int(res * 0.001)}kb_{restriction}.csv')
    if smooth:
        csv_name = csv_name.replace('.csv', '_smoothed.csv')
    if not op.exists(csv_name):
        print(f"Saving A-compartment intervals to: {csv_name}")
        df[csv_columns].to_csv(csv_name, index=False)
    elif force:
        print(f"File {csv_name} already exists. Overwriting.")
        df[csv_columns].to_csv(csv_name, index=False)
    else: 
        print(f"File {csv_name} already exists. Returning DataFrame only.")

    return df
