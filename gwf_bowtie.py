# %% [markdown]
# ---
# title: "gwf_map_reads"
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
# GWF workflow to map Hi-C reads to pairs with `bowtie2`, `samtools`.
# We try to follow Wang2019's parameters. 
#
# How to run:
# conda activate gwf
# gwf -f gwf_map_reads.py status
#
# Workflow:
#   1a bwa_index        : [Reference genome] Index the reference genome with `bwa index`
#   1b sam_index        : [Reference genome] Index the fasta again with `samtools faidx``
#   1c find_rest_sites  : [Reference genome] Find the restriction sites in the reference genome with `hicFindRestSites` from HiCExplorer
#   2  bwa_map          : Map reads (individually) to the reference with `bwa mem`
#   3  build_hic_matrix : Build the interaction matrix from mapped reads (.bam) with `hicBuildMatrix` from HiCExplorer
#
#######################################

# Create a workflow object
gwf = Workflow(defaults={'nodes': 1, 'queue':"normal", 'account':"hic-spermatogenesis"})

#############################################
############### Templates ###################
#############################################

def bowtie_index(ref_genome):
    """Creating a bowtie2 index. Afterwards, bowtie2 only uses these files, and not the original fasta file"""
    threads = 16
    inputs = [ref_genome]
    outputs = [f"{ref_genome}.1.bt2l",
               f"{ref_genome}.2.bt2l",
               f"{ref_genome}.3.bt2l",
               f"{ref_genome}.4.bt2l",
               f"{ref_genome}.rev.1.bt2l",
               f"{ref_genome}.rev.2.bt2l"]
    options = {'cores':threads, 'memory':"32g", 'walltime':"01:00:00"}
    spec=f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
bowtie2-build -f --large-index --threads {threads}  {ref_genome} {ref_genome}
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)


def find_rest_sites(ref_genome, rest_seq, out_bed):
    """Find the restriction sites in the reference genome.
    Used by `hicBuildMatrix` when building the interaction matrix"""
    inputs = [ref_genome]
    outputs = [out_bed]
    options = {'cores':1, 'memory':"5g", 'walltime':"00:20:00"}
    spec = f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
hicFindRestSite --fasta {ref_genome} --searchPattern {rest_seq} --outFile {out_bed}
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)

def bowtie_map(bt2_idx, in_fastq, out_bam):
    """Map reads to the reference genome with bowtie2"""
    threads = 16
    inputs = [in_fastq,
              f"{bt2_idx}.1.bt2l",
               f"{bt2_idx}.2.bt2l",
               f"{bt2_idx}.3.bt2l",
               f"{bt2_idx}.4.bt2l",
               f"{bt2_idx}.rev.1.bt2l",
               f"{bt2_idx}.rev.2.bt2l"]
    outputs = [out_bam]
    options = {'cores':threads, 'memory':"16g", 'walltime':"06:00:00"}
    spec = f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
bowtie2 -x {bt2_idx} --threads {threads} -U {in_fastq} -t --reorder --end-to-end --very-sensitive | \
    samtools view --threads {threads-1} -Shb - > {out_bam}
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)


def build_hic_matrix(bam1, bam2, rest_seq, rest_site_positions, out_matrix, out_qc_folder):
    threads = 8
    inputs = [bam1, bam2, rest_site_positions]
    outputs = [out_matrix, out_qc_folder]
    options = {'cores':threads, 'memory': "128g", 'walltime':"02:00:00"}
    spec = f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
hicBuildMatrix --samFiles {bam1} {bam2} \
    --binSize 10000 40000 100000 \
    --restrictionSequence {rest_seq} \
    --danglingSequence {rest_seq} \
    --restrictionCutFile {rest_site_positions} \
    --threads {threads} \
    --inputBufferSize 100000 \
    -o {out_matrix} \
    --QCfolder ./{out_qc_folder}
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)



#############################################
############### Create targets ##############
#############################################

# Do stuff with the reference genome
ref_genome = "data/links/ucsc_ref/rheMac10.fa.gz"
rest_seq = "GATC"
rest_sites_out = "steps/rest_site_positions.bed"

T1a = gwf.target_from_template(
    f"bowtie_index_{os.path.basename(ref_genome)}", 
    bowtie_index(ref_genome=ref_genome))

T1b = gwf.target_from_template(
    f"find_rest_sites_{os.path.basename(ref_genome)}", 
    find_rest_sites(ref_genome=ref_genome, rest_seq=rest_seq, out_bed=rest_sites_out))


# Map Hi-C reads 
fastq_folder = "data/links/macaque_fastq/"
fastq_files = gwf.glob(os.path.join(fastq_folder, "*.fastq.gz"))


# Pair the files (make sure they have the same base name prefix):
fastq_files.sort()
paired_fastq_files = list(zip(fastq_files[::2], fastq_files[1::2]))

for f1,f2 in paired_fastq_files:
    # Get the base names
    basename_1 = os.path.basename(f1).split('.fast')[0]
    basename_2 = os.path.basename(f2).split('.fast')[0]
    
    # Create the output bam filenames
    out_bam_1 = f"steps/bowtie2/{basename_1}.bam"
    out_bam_2 = f"steps/bowtie2/{basename_2}.bam"

    # Create targets for mapping
    T2a = gwf.target_from_template(f"bowtie_map_{basename_1}", bowtie_map(bt2_idx=ref_genome, in_fastq=f1, out_bam=out_bam_1))
    T2b = gwf.target_from_template(f"bowtie_map_{basename_2}", bowtie_map(bt2_idx=ref_genome, in_fastq=f2, out_bam=out_bam_2))

    # Combine pair names
    pairname = os.path.commonprefix([basename_1, basename_2]).split('_')[0]

    # Create the target for building the matrix (uses out_bam_1 and out_bam_2)
    out_matrix = f"steps/bowtie2/{pairname}_hic.cool"
    out_qc_folder = f"steps/bowtie2/{pairname}_QC"

    T3 = gwf.target_from_template(f"build_hic_matrix_{pairname}", 
                                  build_hic_matrix(bam1=out_bam_1, bam2=out_bam_2, 
                                                   rest_seq=rest_seq,
                                                   rest_site_positions=rest_sites_out, 
                                                   out_matrix=out_matrix, 
                                                   out_qc_folder=out_qc_folder))


    

