#!/bin/bash

# Monte Carlo Simulation Campaign for 6G MANET Blockchain-assisted Routing
# This script runs 50 simulation runs, each with Baseline and Proposed modes

# Default parameters
NODES=${1:-30}
FLOWS=${2:-3}
BLACKHOLES=${3:-7}
SIM_TIME=${4:-60.0}
MAX_RANGE=${5:-150.0}
DEFAULT_SNR=${6:-20.0}
RNG_SEED=${7:-1}
NUM_RUNS=${8:-50}

OUTPUT_FILE="dense_network_results.csv"
BUILD_DIR="/home/katae/study/dp/ns3/ns-3-dev/build/scratch"
SIM_EXECUTABLE="ns3.46-sixg-wigig-sim-default"

# Create campaign log directory with timestamp
CAMPAIGN_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="campaign_logs_${CAMPAIGN_TIMESTAMP}"
mkdir -p "$LOG_DIR"

# Create summary files
DROP_SUMMARY_FILE="$LOG_DIR/drop_summary.csv"
echo "RunID,Mode,PHYDrops,L3Drops,BlackholeL3Drops,RouteSkips,TrustPenalties,MaliciousDrops" > "$DROP_SUMMARY_FILE"

echo "================================================================"
echo "Monte Carlo Simulation Campaign - 6G MANET Blockchain Routing"
echo "================================================================"
echo "Parameters:"
echo "  Nodes: $NODES"
echo "  Flows: $FLOWS"
echo "  Blackholes: $BLACKHOLES"
echo "  Simulation Time: $SIM_TIME seconds"
echo "  Max Radio Range: $MAX_RANGE meters"
echo "  Default SNR: $DEFAULT_SNR dB"
echo "  RNG Seed: $RNG_SEED"
echo "  Number of Runs: $NUM_RUNS"
echo "Output file: $OUTPUT_FILE"
echo "Log directory: $LOG_DIR"
echo "================================================================"
echo ""

# Compile the simulation once
echo "Step 1: Compiling NS-3 simulation..."
cd /home/katae/study/dp/ns3/ns-3-dev
./ns3 build 2>&1 | tail -3
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "ERROR: Compilation failed. Exiting."
    exit 1
fi
cd - > /dev/null
echo "Compilation successful."
echo ""

# Create output file with header (only if it doesn't exist)
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "RunID,Mode,PDR,Latency,AvgHops,MaliciousDrops" > $OUTPUT_FILE
    echo "Created new output file: $OUTPUT_FILE"
    START_RUN=1
else
    echo "Appending to existing output file: $OUTPUT_FILE"
    # Find the last completed run
    LAST_RUN=$(tail -n +2 "$OUTPUT_FILE" 2>/dev/null | awk -F',' '{print $1}' | sort -n | tail -1)
    if [ -z "$LAST_RUN" ] || [ "$LAST_RUN" = "" ]; then
        START_RUN=1
    else
        # Check if last run has both Baseline and Proposed
        BASELINE_COUNT=$(grep -c "^${LAST_RUN},Baseline," "$OUTPUT_FILE" 2>/dev/null || echo "0")
        PROPOSED_COUNT=$(grep -c "^${LAST_RUN},Proposed," "$OUTPUT_FILE" 2>/dev/null || echo "0")
        if [ "$BASELINE_COUNT" -eq 1 ] && [ "$PROPOSED_COUNT" -eq 1 ]; then
            START_RUN=$((LAST_RUN + 1))
            echo "Resuming from run $START_RUN (last completed: $LAST_RUN)"
        else
            START_RUN=$LAST_RUN
            echo "Last run $LAST_RUN incomplete, restarting from run $START_RUN"
        fi
    fi
fi

# Run Monte Carlo simulations
echo "Step 2: Starting Monte Carlo simulation campaign..."
echo "Progress:"
echo "Starting from run $START_RUN to $NUM_RUNS"

for (( run=$START_RUN; run<=$NUM_RUNS; run++ ))
do
    # Progress indicator (always show for first 5 runs, then every 10th)
    if [ $run -le 5 ] || [ $((run % 10)) -eq 0 ]; then
        echo "  Run $run/$NUM_RUNS..."
    fi
    
    # Run Baseline scenario with timeout and error handling
    # OPTIMIZED: Parse directly from stdout, don't write full logs (much faster)
    BASELINE_LOG_FILE="$LOG_DIR/run${run}_baseline.log"
    echo "    → Starting Baseline run $run..."
    BASELINE_FULL_OUTPUT=$(timeout 180 /home/katae/study/dp/ns3/ns-3-dev/build/scratch/$SIM_EXECUTABLE \
        --numNodes=$NODES --numFlows=$FLOWS --numBlackholes=$BLACKHOLES \
        --simTime=$SIM_TIME --maxRadioRange=$MAX_RANGE --defaultSnr=$DEFAULT_SNR \
        --RngSeed=$RNG_SEED --RngRun=$run --useBlockchain=false 2>&1)
    BASELINE_EXIT_CODE=${PIPESTATUS[0]}
    if [ $BASELINE_EXIT_CODE -ne 0 ]; then
        echo "    WARNING: Baseline run $run exited with code $BASELINE_EXIT_CODE"
    fi
    
    # Save only summary lines to log file (much smaller)
    echo "$BASELINE_FULL_OUTPUT" | grep -E "(RESULT_DATA|DROP_SUMMARY)" > "$BASELINE_LOG_FILE"
    
    # Extract metrics directly from output (faster than reading file)
    BASELINE_OUTPUT=$(echo "$BASELINE_FULL_OUTPUT" | grep "RESULT_DATA")
    BASELINE_PDR=$(echo "$BASELINE_OUTPUT" | awk -F', ' '{print $4}')
    BASELINE_LATENCY=$(echo "$BASELINE_OUTPUT" | awk -F', ' '{print $5}')
    BASELINE_AVGHOPS=$(echo "$BASELINE_OUTPUT" | awk -F', ' '{print $6}')
    BASELINE_MALICIOUS=$(echo "$BASELINE_OUTPUT" | awk -F', ' '{print $7}')
    
    # Extract drop summary directly from output (faster)
    BASELINE_DROP_SUMMARY=$(echo "$BASELINE_FULL_OUTPUT" | grep "^\[DROP_SUMMARY\]" | tail -1)
    if [ -n "$BASELINE_DROP_SUMMARY" ]; then
        # Parse drop summary: [DROP_SUMMARY] RunID=X | Mode=Baseline | PHYDrops=X | L3Drops=X | BlackholeL3Drops=X | RouteSkips=X | TrustPenalties=X | MaliciousDrops=X
        BASELINE_PHYDROPS=$(echo "$BASELINE_DROP_SUMMARY" | sed -n 's/.*PHYDrops=\([0-9]*\).*/\1/p')
        BASELINE_L3DROPS=$(echo "$BASELINE_DROP_SUMMARY" | sed -n 's/.*L3Drops=\([0-9]*\).*/\1/p')
        BASELINE_BLACKHOLE_L3DROPS=$(echo "$BASELINE_DROP_SUMMARY" | sed -n 's/.*BlackholeL3Drops=\([0-9]*\).*/\1/p')
        BASELINE_ROUTE_SKIPS=$(echo "$BASELINE_DROP_SUMMARY" | sed -n 's/.*RouteSkips=\([0-9]*\).*/\1/p')
        BASELINE_TRUST_PENALTIES=$(echo "$BASELINE_DROP_SUMMARY" | sed -n 's/.*TrustPenalties=\([0-9]*\).*/\1/p')
        
        # Default to 0 if not found
        BASELINE_PHYDROPS=${BASELINE_PHYDROPS:-0}
        BASELINE_L3DROPS=${BASELINE_L3DROPS:-0}
        BASELINE_BLACKHOLE_L3DROPS=${BASELINE_BLACKHOLE_L3DROPS:-0}
        BASELINE_ROUTE_SKIPS=${BASELINE_ROUTE_SKIPS:-0}
        BASELINE_TRUST_PENALTIES=${BASELINE_TRUST_PENALTIES:-0}
    else
        BASELINE_PHYDROPS=0
        BASELINE_L3DROPS=0
        BASELINE_BLACKHOLE_L3DROPS=0
        BASELINE_ROUTE_SKIPS=0
        BASELINE_TRUST_PENALTIES=0
    fi
    
    # Validate and append Baseline result
    if [ -z "$BASELINE_OUTPUT" ] || [ -z "$BASELINE_PDR" ]; then
        echo "    WARNING: Baseline run $run failed, using 0.00,0.00,0.00,0"
        echo "$run,Baseline,0.00,0.00,0.00,0" >> $OUTPUT_FILE
        echo "$run,Baseline,0,0,0,0,0,0" >> "$DROP_SUMMARY_FILE"
    else
        # Use explicit file descriptor to ensure immediate write
        { echo "$run,Baseline,$BASELINE_PDR,$BASELINE_LATENCY,$BASELINE_AVGHOPS,$BASELINE_MALICIOUS"; } >> $OUTPUT_FILE
        { echo "$run,Baseline,$BASELINE_PHYDROPS,$BASELINE_L3DROPS,$BASELINE_BLACKHOLE_L3DROPS,$BASELINE_ROUTE_SKIPS,$BASELINE_TRUST_PENALTIES,$BASELINE_MALICIOUS"; } >> "$DROP_SUMMARY_FILE"
    fi
    
    # Run Proposed scenario with timeout and error handling
    # OPTIMIZED: Parse directly from stdout, don't write full logs (much faster)
    PROPOSED_LOG_FILE="$LOG_DIR/run${run}_proposed.log"
    echo "    → Starting Proposed run $run..."
    PROPOSED_FULL_OUTPUT=$(timeout 180 /home/katae/study/dp/ns3/ns-3-dev/build/scratch/$SIM_EXECUTABLE \
        --numNodes=$NODES --numFlows=$FLOWS --numBlackholes=$BLACKHOLES \
        --simTime=$SIM_TIME --maxRadioRange=$MAX_RANGE --defaultSnr=$DEFAULT_SNR \
        --RngSeed=$RNG_SEED --RngRun=$run --useBlockchain=true 2>&1)
    PROPOSED_EXIT_CODE=${PIPESTATUS[0]}
    if [ $PROPOSED_EXIT_CODE -ne 0 ]; then
        echo "    WARNING: Proposed run $run exited with code $PROPOSED_EXIT_CODE"
    fi
    
    # Save only summary lines to log file (much smaller)
    echo "$PROPOSED_FULL_OUTPUT" | grep -E "(RESULT_DATA|DROP_SUMMARY)" > "$PROPOSED_LOG_FILE"
    
    # Extract metrics directly from output (faster than reading file)
    PROPOSED_OUTPUT=$(echo "$PROPOSED_FULL_OUTPUT" | grep "RESULT_DATA")
    PROPOSED_PDR=$(echo "$PROPOSED_OUTPUT" | awk -F', ' '{print $4}')
    PROPOSED_LATENCY=$(echo "$PROPOSED_OUTPUT" | awk -F', ' '{print $5}')
    PROPOSED_AVGHOPS=$(echo "$PROPOSED_OUTPUT" | awk -F', ' '{print $6}')
    PROPOSED_MALICIOUS=$(echo "$PROPOSED_OUTPUT" | awk -F', ' '{print $7}')
    
    # Extract drop summary directly from output (faster)
    PROPOSED_DROP_SUMMARY=$(echo "$PROPOSED_FULL_OUTPUT" | grep "^\[DROP_SUMMARY\]" | tail -1)
    if [ -n "$PROPOSED_DROP_SUMMARY" ]; then
        # Parse drop summary
        PROPOSED_PHYDROPS=$(echo "$PROPOSED_DROP_SUMMARY" | sed -n 's/.*PHYDrops=\([0-9]*\).*/\1/p')
        PROPOSED_L3DROPS=$(echo "$PROPOSED_DROP_SUMMARY" | sed -n 's/.*L3Drops=\([0-9]*\).*/\1/p')
        PROPOSED_BLACKHOLE_L3DROPS=$(echo "$PROPOSED_DROP_SUMMARY" | sed -n 's/.*BlackholeL3Drops=\([0-9]*\).*/\1/p')
        PROPOSED_ROUTE_SKIPS=$(echo "$PROPOSED_DROP_SUMMARY" | sed -n 's/.*RouteSkips=\([0-9]*\).*/\1/p')
        PROPOSED_TRUST_PENALTIES=$(echo "$PROPOSED_DROP_SUMMARY" | sed -n 's/.*TrustPenalties=\([0-9]*\).*/\1/p')
        
        # Default to 0 if not found
        PROPOSED_PHYDROPS=${PROPOSED_PHYDROPS:-0}
        PROPOSED_L3DROPS=${PROPOSED_L3DROPS:-0}
        PROPOSED_BLACKHOLE_L3DROPS=${PROPOSED_BLACKHOLE_L3DROPS:-0}
        PROPOSED_ROUTE_SKIPS=${PROPOSED_ROUTE_SKIPS:-0}
        PROPOSED_TRUST_PENALTIES=${PROPOSED_TRUST_PENALTIES:-0}
    else
        PROPOSED_PHYDROPS=0
        PROPOSED_L3DROPS=0
        PROPOSED_BLACKHOLE_L3DROPS=0
        PROPOSED_ROUTE_SKIPS=0
        PROPOSED_TRUST_PENALTIES=0
    fi
    
    # Validate and append Proposed result
    if [ -z "$PROPOSED_OUTPUT" ] || [ -z "$PROPOSED_PDR" ]; then
        echo "    WARNING: Proposed run $run failed, using 0.00,0.00,0.00,0"
        { echo "$run,Proposed,0.00,0.00,0.00,0"; } >> $OUTPUT_FILE
        { echo "$run,Proposed,0,0,0,0,0,0"; } >> "$DROP_SUMMARY_FILE"
    else
        # Use explicit file descriptor to ensure immediate write
        { echo "$run,Proposed,$PROPOSED_PDR,$PROPOSED_LATENCY,$PROPOSED_AVGHOPS,$PROPOSED_MALICIOUS"; } >> $OUTPUT_FILE
        { echo "$run,Proposed,$PROPOSED_PHYDROPS,$PROPOSED_L3DROPS,$PROPOSED_BLACKHOLE_L3DROPS,$PROPOSED_ROUTE_SKIPS,$PROPOSED_TRUST_PENALTIES,$PROPOSED_MALICIOUS"; } >> "$DROP_SUMMARY_FILE"
    fi
    
    # CRITICAL: Force flush file buffers to disk
    # Close file descriptors to ensure data is written
    exec 1>&1 2>&2
    
    # Progress message after each pair
    echo "    ✓ Run $run/$NUM_RUNS complete (Baseline + Proposed saved)"
    
    # Verify files were written
    if [ -f "$OUTPUT_FILE" ]; then
        LINES=$(wc -l < "$OUTPUT_FILE" 2>/dev/null || echo "0")
        echo "    → Output file has $LINES lines (expected: $((1 + run * 2)))"
    fi
done

echo ""
echo "================================================================"
echo "Monte Carlo Simulation Campaign Complete!"
echo "================================================================"
echo "Results saved to: $OUTPUT_FILE"
echo "Drop summary saved to: $DROP_SUMMARY_FILE"
echo "Detailed logs saved to: $LOG_DIR/"
echo "Total runs: $NUM_RUNS (Baseline + Proposed = $((NUM_RUNS * 2)) total simulations)"
echo ""
echo "Summary statistics:"
echo "  Baseline PDR:"
awk -F',' '$2=="Baseline" {sum+=$3; count++} END {if(count>0) printf "    Average: %.2f%%\n", sum/count}' $OUTPUT_FILE
echo "  Proposed PDR:"
awk -F',' '$2=="Proposed" {sum+=$3; count++} END {if(count>0) printf "    Average: %.2f%%\n", sum/count}' $OUTPUT_FILE
echo "  Baseline Latency:"
awk -F',' '$2=="Baseline" && $4!="0.00" {sum+=$4; count++} END {if(count>0) printf "    Average: %.2f ms\n", sum/count}' $OUTPUT_FILE
echo "  Proposed Latency:"
awk -F',' '$2=="Proposed" && $4!="0.00" {sum+=$4; count++} END {if(count>0) printf "    Average: %.2f ms\n", sum/count}' $OUTPUT_FILE
echo "================================================================"
