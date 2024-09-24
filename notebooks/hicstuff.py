import os
import glob
import matplotlib.pyplot as plt
import natsort 
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
    print(f"Plotting all images in '{os.path.join(image_folder, f'*{suffix}')}':")
    image_files = glob.glob(os.path.join(image_folder, f'*{suffix}'))
    image_files = natsort.natsorted(image_files)


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

