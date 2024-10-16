#!/bin/bash

# Define the function
process_bwa_log() {
    log_file=$1    # The bwa mem log file
    srrid=$2       # The SRR ID to match in the SRA-RunTable.csv
    csv_file="/home/sojern/hic-spermatogenesis/people/sojern/hic-spermatogenesis/data/SraRunTable.txt"  # Path to the SRA-RunTable file

    # Extract the 'bases' corresponding to the given SRRID from the CSV (assuming comma-separated and SRRID in the first column, Bases in the fourth column)
    bases=$(awk -F',' -v id="$srrid" '$1 == id {print $4}' "$csv_file")
    nreads=$(echo "$bases / 300" | bc)

    echo $bases bases, $nreads reads in $srrid

    # If bases is empty, show an error
    if [[ -z "$bases" ]]; then
        echo "SRRID $srrid not found in $csv_file"
        return 1
    fi

    # Grep for relevant lines from the log and calculate the sum of base pairs, divided by the number of bases
    grep '\[M::process\]' "$log_file" | awk -F'[()]' -v bases="$bases" '{sum += $2} END {if (bases > 0) print sum / bases " progress"; else print "No valid base count"}'
}

# Call the function with parameters
# Example usage: process_bwa_log "bwa_log.txt" "SRR6502335"
process_bwa_log "$1" "$2"
