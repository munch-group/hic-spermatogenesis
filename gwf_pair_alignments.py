# %% [markdown]
# ---
# title: "gwf_bowtie_local"
# author: Søren Jørgensen
# date: last-modified
# execute: 
#   enabled: false
# ---

# %%
from gwf import *
import glob
import os

#######################################
#
# GWF workflow to pair alignments from mate-pair sequencing, after mapping to the reference individually.
# After mapping, the mate-pairs are merged with `samtools merge` (another workflow) and then parsed with `pairtools parse`. 
#
# How to run:
# conda activate gwf
# gwf -f gwf_gwf_pair_alignments.py status
#
# Workflow:
#   1   pairtools parse : Parse the fastq files into pairs (after merging with `samtools merge`)
#
# Footnote: always activate the conda environment before running the workflow:
# source $(conda info --base)/etc/profile.d/conda.sh
# conda activate env_name
#######################################

# Create a workflow object
gwf = Workflow(defaults={'nodes': 1, 'queue':"normal", 'account':"hic-spermatogenesis"})

#############################################
############### Templates ###################
#############################################

def pair_sort_alignments(bam_merged, sorted_pairs):
    """Pair the merged alignments from mate-pair sequencing with `pairtools parse`"""
    inputs = [bam_merged]
    outputs = [f"{bam_merged}_parsed.stats", 
               sorted_pairs]
    options = {'cores':12, 'memory':"4g", 'walltime':"01:00:00"}
    spec=f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
pairtools parse \
    -c {chromsizes} \
    --drop-sam --drop-seq \
    --output-stats {bam_merged}_parsed.stats \
    --add-columns mapq \
    --assembly rheMac10 --no-flip \
    --walks-policy mask 
    {bam_merged} | \
pairtools sort -o {sorted_pairs} 
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)



#############################################
################ Targets ####################
#############################################

# Define the chromsizes file
chromsizes = "data/links/ucsc_ref/misc/rheMac10.chrom.sizes.gz"

# Find the merged bam files
merged_bams = gwf.glob("steps/bowtie2/local/bamfiles/paired/*_paired.bam")

