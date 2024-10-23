# %% [markdown]
# ---
# title: "group_runs"
# author: Søren Jørgensen
# date: last-modified
# execute: 
#   enabled: false
# ---

# %% [markdown]
# # Group runs
# 
# This script groups the runs by tissue type and replicates.


# %% [python]
import pandas as pd
import os
import os.path as op
from pprintpp import pprint as pp

# Define subdirs for tissue type, strip_whitespace and make lowercase
sra_runtable = pd.read_csv("../data/SraRunTable-2.txt")
reads_subdirs = set(sra_runtable["source_name"])

# Make a dict mapping the tissue type ['source_name'] to the SRR IDs ['Run']
tissue_dict = {tissue: sra_runtable[sra_runtable["source_name"]==tissue]["Run"].tolist() for tissue in reads_subdirs}

# Now map the IDs to 'Biosample' column (make a 'replicate' column, 'repX' for short, below source_name)
df = pd.read_csv("../data/SraRunTable-2.txt").groupby(["source_name", "BioSample"])[['Run']]
df = df.agg(lambda x: list(x))['Run']
lookup_table = df.agg(lambda x: list(x)).to_dict()

#print(lookup_df.keys())

#Look up the tissue type for each read

# Example: Loop over levels of the MultiIndex and the values in the DataFrame
for source_name in df.index.get_level_values(0).unique():  # Loop over source_name
    for biosample in df.loc[source_name].index:  # Loop over BioSample for each source_name
        srr_list = df.loc[(source_name, biosample)]  # Get the SRR list for this combination
        for srr in srr_list:  # Loop over each SRR ID in the list
            print(f"Source: {source_name}, BioSample: {biosample}, SRR ID: {srr}")

# %%
