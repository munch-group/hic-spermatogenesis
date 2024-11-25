# %% [markdown]
# ---
# title: "gwf_hiccorrect"
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
# GWF workflow to 
#
# How to run:
# conda activate gwf
# gwf -f gwf_hiccorrect.py status
#
# Workflow:
#
#######################################

# Create a workflow object
gwf = Workflow(defaults={'nodes': 1, 'queue':"normal", 'account':"hic-spermatogenesis"})

#############################################
############### Templates ###################
#############################################

def hiccorrect(in_matrix, out_matrix, mem, thresholds):
    """Correct Hi-C data with HiCExplorer's hicCorrectMatrix"""
    inputs = [in_matrix]
    outputs = [out_matrix]
    options = {'cores':1, 'memory':mem, 'walltime':"04:00:00"}
    spec=f"""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hic
hicCorrectMatrix correct \
    -m {in_matrix} -o {out_matrix} \
    --correctionMethod ICE \
    --filterThreshold {thresholds[0]} {thresholds[1]} \
    --perchr \
    --verbose
"""
    return AnonymousTarget(inputs=inputs, outputs=outputs, options=options, spec=spec)

#############################################
############### Targets #####################
#############################################

base_dir = "steps/bowtie2/local/matrices"

# 10kb resolution (a LOT of memory is needed) --maybe not??? (updated values after inspecting target on jobinfo)
in_10kb = os.path.join(base_dir, "normsm_filtered_pooled_10kb.cool")
out_10kb = os.path.join(base_dir, "normsm_filtered_pooled_10kb_corrected.cool")
gwf.target_from_template("hiccorrect_10kb", 
                         hiccorrect(
                             in_matrix=in_10kb,
                             out_matrix=out_10kb,
                             mem="32g",
                             thresholds=(-2, 5)
                             )
                        )

# 40kb resolution (a LOT of memory is needed) --maybe not??? (updated values after inspecting target on jobinfo)
in_40kb = os.path.join(base_dir, "normsm_filtered_pooled_40kb.cool")
out_40kb = os.path.join(base_dir, "normsm_filtered_pooled_40kb_corrected.cool")
gwf.target_from_template("hiccorrect_40kb",
                         hiccorrect(
                             in_matrix=in_40kb,
                             out_matrix=out_40kb,
                             mem="16g",
                             thresholds=(-1.5, 5)
                             )
                        )


# 50kb resolution (a bit less memory is needed) --maybe not??? (updated values after inspecting target on jobinfo)
in_50kb = os.path.join(base_dir, "normsm_filtered_pooled_50kb.cool")
out_50kb = os.path.join(base_dir, "normsm_filtered_pooled_50kb_corrected.cool")
gwf.target_from_template("hiccorrect_50kb", 
                         hiccorrect(
                             in_matrix=in_50kb,
                             out_matrix=out_50kb,
                             mem="16g",
                             thresholds=(-1.5, 5)
                             )
                        )

# 100kb resolution (still a large amount of memory is needed) --maybe not??? (updated values after inspecting target on jobinfo)
in_100kb = os.path.join(base_dir, "normsm_filtered_pooled_100kb.cool")
out_100kb = os.path.join(base_dir, "normsm_filtered_pooled_100kb_corrected.cool")
gwf.target_from_template("hiccorrect_100kb", 
                         hiccorrect(
                             in_matrix=in_100kb,
                             out_matrix=out_100kb,
                             mem="8g",
                             thresholds=(-1.5, 5)
                             )
                        )
