#!/usr/bin/env bash
# Phase 4b sensitivity collection campaign.
# 2 reference models × 8 prompt variants × 5 runs each = 80 records.
# See ARCHITECTURE.md §5.3.

set -euo pipefail

MODELS=("claude-opus-4-6" "openai/gpt-4o")
VARIANTS=("v1_s1" "v1_s2" "v1_s3" "v1_s4" "v1_s5" "v1_s6" "v1_s7" "v1_s8")
RUNS=5
DOMAIN="family"

total=$((${#MODELS[@]} * ${#VARIANTS[@]} * RUNS))
echo "Phase 4b sensitivity collection"
echo "  Models:   ${MODELS[*]}"
echo "  Variants: ${#VARIANTS[@]}"
echo "  Runs/variant: $RUNS"
echo "  Total records: $total"
echo ""

completed=0
for model in "${MODELS[@]}"; do
    for variant in "${VARIANTS[@]}"; do
        echo "=== $model × $variant ($RUNS runs) ==="
        uv run python scripts/collect.py \
            --domain "$DOMAIN" \
            --model "$model" \
            --prompt-version "$variant" \
            --runs "$RUNS"
        completed=$((completed + RUNS))
        echo "  Progress: $completed / $total"
        echo ""
    done
done

echo "Sensitivity collection complete: $completed records."
