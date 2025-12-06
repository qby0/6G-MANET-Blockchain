#!/bin/bash
# Script for running Baseline and Proposed routing experiments

# Configuration
OUTPUT_DIR="results"
NUM_NODES=25
SIM_TIME=30.0  # "Line of Fire" strategy - 30 seconds for traffic flow
NUM_FLOWS=1  # Single flow for deterministic comparison
AREA_SIZE=200.0  # 200m x 200m for 5x5 grid (50m spacing)
SEED=1

echo "=========================================="
echo "6G MANET Blockchain Routing Experiments"
echo "=========================================="
echo ""

# Create output directory
mkdir -p $OUTPUT_DIR

# Experiment 1: Baseline routing
echo "Running Baseline routing experiment..."
python3 src/sim/main_sim.py \
    --mode baseline \
    --num-nodes $NUM_NODES \
    --sim-time $SIM_TIME \
    --num-flows $NUM_FLOWS \
    --area-size $AREA_SIZE \
    --output-dir $OUTPUT_DIR \
    --seed $SEED

if [ $? -ne 0 ]; then
    echo "Error: Baseline experiment failed!"
    exit 1
fi

echo ""
echo "Baseline experiment completed!"
echo ""

# Experiment 2: Proposed routing
echo "Running Proposed (Blockchain-assisted) routing experiment..."
python3 src/sim/main_sim.py \
    --mode proposed \
    --num-nodes $NUM_NODES \
    --sim-time $SIM_TIME \
    --num-flows $NUM_FLOWS \
    --area-size $AREA_SIZE \
    --output-dir $OUTPUT_DIR \
    --seed $SEED

if [ $? -ne 0 ]; then
    echo "Error: Proposed experiment failed!"
    exit 1
fi

echo ""
echo "Proposed experiment completed!"
echo ""

# Generate visualization
echo "Generating comparison plots..."
python3 plot_results.py \
    --baseline $OUTPUT_DIR/baseline_metrics.json \
    --proposed $OUTPUT_DIR/proposed_metrics.json \
    --output-dir $OUTPUT_DIR \
    --plot-type combined

if [ $? -ne 0 ]; then
    echo "Warning: Plot generation failed!"
else
    echo "Plots generated successfully!"
fi

echo ""
echo "=========================================="
echo "All experiments completed!"
echo "Results are in: $OUTPUT_DIR"
echo "=========================================="

