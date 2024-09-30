import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from natsort import natsorted
from PIL import Image

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
    print(f"Plotting all images in '{os.path.join(image_folder, f'*{suffix}')}':")
    image_files = glob.glob(os.path.join(image_folder, f'*{suffix}'))
    image_files = natsorted(image_files,)


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
    plt.show()

