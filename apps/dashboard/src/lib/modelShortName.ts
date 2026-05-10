/**
 * Shared model short name mapping.
 *
 * Extracted from MDSPlot.tsx at T7 so ModelSelector and MDSPlot
 * use the same map rather than maintaining separate copies.
 *
 * The map is keyed by canonical model_id. Models not in the map
 * fall back to the last path segment after "/" or the full model_id.
 */

export const MODEL_SHORT_NAMES: Record<string, string> = {
  "claude-opus-4-6": "Claude Opus 4.6",
  "claude-sonnet-4-6": "Claude Sonnet 4.6",
  "deepseek/deepseek-v3.2": "DeepSeek v3.2",
  "google/gemini-2.5-pro": "Gemini 2.5 Pro",
  "meta-llama/llama-4-maverick": "Llama 4 Maverick",
  "microsoft/phi-4": "Phi-4",
  "mistralai/mistral-large-2512": "Mistral Large",
  "mistralai/mistral-small-2603": "Mistral Small",
  "openai/gpt-5.4": "GPT-5.4",
  "openai/gpt-5.4-mini": "GPT-5.4 mini",
  "x-ai/grok-4": "Grok 4",
};

/**
 * Returns a short display name for a model_id.
 * Falls back to the last path segment or the full id if no mapping exists.
 */
export function modelShortName(modelId: string): string {
  if (MODEL_SHORT_NAMES[modelId]) return MODEL_SHORT_NAMES[modelId];
  const parts = modelId.split("/");
  return parts[parts.length - 1];
}
