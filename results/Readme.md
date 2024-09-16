
# Result files

## Quality control

`hicBuildMatrix` was used to generate the matrices for the Hi-C data, doing some quality control in the process. The quality control results are available as a html file in each folder.

To preview the html files, prepend the following to the URL of the `hicQC.html` in each folder: `https://html-preview.github.io/?url=`

Or click the links below: 

- [Preview sample SRR6502335 QC results](https://html-preview.github.io/?url=https://github.com/munch-group/hic-spermatogenesis/blob/main/results/SRR6502335_QC/hicQC.html)

| Name                 | Count       | Percent |
|----------------------|-------------|---------|
| Sequenced reads      | 244,003,806 | 100     |
| Mappable, highQ+uniq | 164,715,495 | 67.5    |
| Hi-C contacts        | 110,459,727 | 45.27   |
| Inter chromosomal    | 28,350,411  | 25.67   |
| Intra short          | 14,384,188  | 13.02   |
| Intra long           | 67,725,128  | 61.31   |

- [Preview sample SRR6502336 QC results](https://html-preview.github.io/?url=https://github.com/munch-group/hic-spermatogenesis/blob/main/results/SRR6502336_QC/hicQC.html)

| Name                 | Count       | Percent |
|----------------------|-------------|---------|
| Sequenced reads      | 217,066,567 | 100     |
| Mappable, highQ+uniq | 147,553,720 | 68      |
| Hi-C contacts        | 94,317,987  | 43.45   |
| Inter chromosomal    | 24,058,490  | 25.51   |
| Intra short          | 12,514,652  | 13.27   |
| Intra long           | 57,744,845  | 61.22   |

- [Preview sample SRR6502337 QC results](https://html-preview.github.io/?url=https://github.com/munch-group/hic-spermatogenesis/blob/main/results/SRR6502337_QC/hicQC.html)
- [Preview sample SRR6502338 QC results](https://html-preview.github.io/?url=https://github.com/munch-group/hic-spermatogenesis/blob/main/results/SRR6502338_QC/hicQC.html)
- [Preview sample SRR6502339 QC results](https://html-preview.github.io/?url=https://github.com/munch-group/hic-spermatogenesis/blob/main/results/SRR6502339_QC/hicQC.html)

### Guidelines from HiCExplorer:

The `hicBuildMatrix` command generates a bam file and a matrix file for the Hi-C data. The bam file contains only the valid Hi-C read pairs, which can be used to assess the quality of the Hi-C library on the genome browser. A good Hi-C library should have an abundance of reads near the restriction fragment sites.

In the QC folder, an html file is saved with plots that provide useful information for the quality control of the Hi-C sample. This includes metrics such as the number of valid pairs, duplicated pairs, and self-ligations. Typically, only 25%-40% of the reads are considered valid and used to build the Hi-C matrix, as reads on repetitive regions are discarded.

One important quality control measurement is the interchromosomal fraction of reads, which indirectly measures random Hi-C contacts. A good Hi-C library should have less than 10% interchromosomal contacts. The hicQC module can be used to compare the quality control measures across different samples.