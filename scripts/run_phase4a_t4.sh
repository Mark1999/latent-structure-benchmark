#!/usr/bin/env bash
# Phase 4a T4 — full 12-model x 2-domain x N=5 collection runner
# Architecture ref: docs/status/2026-04-22-phase4a-kickoff-architect-verdict.md Amendment A
# Mode: single_pass (Amendment A.1 corrects original cross_model label)
# 5 parallel streams, each writing its own output file to avoid concurrent-append races.
# After all streams finish, stream files are merged into data/raw/informants.jsonl.

set -u  # NOT -e — continue past cell failures, do not abort

export PATH="/home/lsb/.local/bin:$PATH"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p data/raw logs

run_stream () {
  local name="$1"; shift
  local log="logs/phase4a-t4-${name}.log"
  local out="data/raw/informants-t4-${name}.jsonl"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] STREAM $name START" >> "$log"
  for pair in "$@"; do
    model="${pair%%|*}"
    domain="${pair##*|}"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] START $model x $domain" >> "$log"
    uv run python scripts/collect.py \
      --mode single_pass \
      --domain "$domain" \
      --model "$model" \
      --runs 5 \
      --output "$out" \
      >> "$log" 2>&1
    local rc=$?
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] END   $model x $domain rc=$rc" >> "$log"
  done
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] STREAM $name COMPLETE" >> "$log"
}

START_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Phase 4a T4 run started at $START_TS"

run_stream anthropic \
  "anthropic/claude-opus-4.6|family" \
  "anthropic/claude-opus-4.6|holidays" \
  "anthropic/claude-sonnet-4.6|family" \
  "anthropic/claude-sonnet-4.6|holidays" &
PID_ANTHROPIC=$!

run_stream openai \
  "openai/gpt-5.4|family" \
  "openai/gpt-5.4|holidays" \
  "openai/gpt-5.4-mini|family" \
  "openai/gpt-5.4-mini|holidays" &
PID_OPENAI=$!

run_stream google \
  "google/gemini-2.5-pro|family" \
  "google/gemini-2.5-pro|holidays" &
PID_GOOGLE=$!

run_stream xai \
  "x-ai/grok-4|family" \
  "x-ai/grok-4|holidays" &
PID_XAI=$!

run_stream openrouter \
  "meta-llama/llama-4-maverick|family" \
  "meta-llama/llama-4-maverick|holidays" \
  "mistralai/mistral-large-2512|family" \
  "mistralai/mistral-large-2512|holidays" \
  "mistralai/mistral-small-2603|family" \
  "mistralai/mistral-small-2603|holidays" \
  "deepseek/deepseek-v3.2|family" \
  "deepseek/deepseek-v3.2|holidays" \
  "qwen/qwen3.6-plus|family" \
  "qwen/qwen3.6-plus|holidays" \
  "z-ai/glm-5.1|family" \
  "z-ai/glm-5.1|holidays" &
PID_OPENROUTER=$!

wait $PID_ANTHROPIC $PID_OPENAI $PID_GOOGLE $PID_XAI $PID_OPENROUTER

END_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "ALL STREAMS COMPLETE at $END_TS"
