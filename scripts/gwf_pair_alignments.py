# %% [markdown]
# ---
# title: "gwf_pair_alignments"
# author: Søren Jørgensen
# date: last-modified
# execute: 
#   enabled: false
# ---

# %%
from gwf import *
import glob
import os.path as op

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

def pair_sort_alignments(chromsizes, bam_merged, sorted_pairs):
    """Pair the merged alignments from mate-pair sequencing with `pairtools parse`"""
    inputs = [bam_merged]
    outputs = [f"{bam_merged}_parsed.stats", 
               sorted_pairs]
    options = {'cores':12, 'memory':"16g", 'walltime':"03:00:00"}
    spec=f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
pairtools parse \
    -c {chromsizes} \
    --drop-sam --drop-seq \
    --output-stats {bam_merged}_parsed.stats \
    --add-columns mapq \
    --assembly rheMac10 --no-flip \
    --walks-policy mask \
    {bam_merged} | \
pairtools sort -o {sorted_pairs} 
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)

def select_pairs(chromsizes, sorted_pairs, selected_pairs):
    """Select the pairs with `pairtools select`"""
    inputs = [sorted_pairs]
    outputs = [selected_pairs]
    options = {'cores':12, 'memory':"16g", 'walltime':"03:00:00"}
    spec=f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
pairtools select \
    --output {selected_pairs} \
    --chrom-subset {chromsizes} \
    {sorted_pairs}
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)

def dedup(sorted_pairs, ):
    """Deduplicate the sorted pairs with `pairtools dedup`"""
    pairs_prefix = sorted_pairs.split(".sorted")[0]
    inputs = [sorted_pairs]
    outputs = [f"{pairs_prefix}.nodups.pairs.gz",
               f"{pairs_prefix}.nodups.bam",
               f"{pairs_prefix}.unmapped.pairs.gz",
               f"{pairs_prefix}.unmapped.bam",
               f"{pairs_prefix}.dups.pairs.gz",
               f"{pairs_prefix}.dups.bam",
               f"{pairs_prefix}.dedup.stats"]
    options = {'cores':12, 'memory': "4g", 'walltime': "01:00:00"}
    spec = f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
pairtools dedup \
    --max-mismatch 3 \
    --mark-dups \
    --output \
        >(pairtools split \
            --output-pairs {pairs_prefix}.nodups.pairs.gz \
            --output-sam {pairs_prefix}.nodups.bam \
         ) \
    --output-unmapped \
        >( pairtools split \
            --output-pairs {pairs_prefix}.unmapped.pairs.gz \
            --output-sam {pairs_prefix}.unmapped.bam \
         ) \
    --output-dups \
        >( pairtools split \
            --output-pairs {pairs_prefix}.dups.pairs.gz \
            --output-sam {pairs_prefix}.dups.bam \
            ) \
    --output-stats {pairs_prefix}.dedup.stats \
    {sorted_pairs}

    """
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)


#############################################
################ Targets ####################
#############################################

# Define the chromsizes file
chromsizes = "data/links/ucsc_ref/misc/rheMac10.chrom.sizes"

# Find the merged bam files
merged_bams = gwf.glob("steps/bowtie2/local/bamfiles/paired/*_paired.bam")

sorted_bams = sorted(merged_bams)


for inbam in sorted_bams:
    base = op.basename(inbam)
    prefix = base.split("_paired")[0]

    # Sort the pairs    
    outdir = "steps/bowtie2/local/bamfiles/paired/"
    outfile = f"{base.split("_paired")[0]}" + ".sorted.pairs.gz"
    out_sorted_pairs = op.join(outdir, outfile)

    gwf.target_from_template(f"pair_sort_{prefix}",
                            pair_sort_alignments(chromsizes, inbam, out_sorted_pairs))
    
    # Select the pairs (filter out unplaced contigs)
    chromsizes = "data/links/ucsc_ref/misc/rheMac10.filtered.chrom.sizes"
    selected_pairs = out_sorted_pairs.replace(".sorted", ".filtered")

    gwf.target_from_template(f"select_{prefix}",
                            select_pairs(chromsizes, out_sorted_pairs, selected_pairs))

    # Deduplicate the pairs
    gwf.target_from_template(f"dedup_{prefix}",
                            dedup(out_sorted_pairs))