/**
 * Permalink codec — encodes and decodes view state into a URL.
 *
 * Format: ?domain={slug}&models={a,b,c}#mds
 *
 * - `domain` search param: the active domain slug
 * - `models` search param: comma-separated selectedModels list (URL-encoded per-model)
 * - URL fragment: the active viz tab (e.g. #mds)
 *
 * The encode/decode pair round-trips cleanly:
 *   decodePermalink(encodePermalink(state)) deep-equals the original state.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 */

export interface PermalinkState {
  domain: string;
  models: string[];
  /** Phase 5: "mds". Phase 6 T7: "freelist". Phase 6 T5: "similarity". Phase 9a T10: "centrality". Phase 9a T9: "piles". */
  vizTab: "mds" | "freelist" | "similarity" | "centrality" | "piles";
}

/**
 * Encode a PermalinkState into a URL string.
 * Returns the full search+hash portion (including leading "?").
 * e.g. "?domain=family&models=claude-opus-4-6%2Copenai%2Fgpt-5.4#mds"
 *
 * Each model_id is individually URL-encoded so "/" chars become "%2F".
 * The models param itself is joined by comma (before encoding the models param value).
 * We URL-encode the entire models string as a single param value.
 */
export function encodePermalink(state: PermalinkState): string {
  const params = new URLSearchParams();
  params.set("domain", state.domain);
  // Join models with comma; URLSearchParams.set encodes the whole value including commas.
  params.set("models", state.models.join(","));
  const search = "?" + params.toString();
  const hash = "#" + state.vizTab;
  return search + hash;
}

/**
 * Decode a URL search+hash string into a PermalinkState.
 * Returns null if the string is missing required fields or is malformed.
 *
 * @param searchAndHash - e.g. "?domain=family&models=a,b,c#mds"
 */
export function decodePermalink(searchAndHash: string): PermalinkState | null {
  if (!searchAndHash) return null;

  try {
    // Split on "#" to extract hash.
    const hashIndex = searchAndHash.indexOf("#");
    const searchPart = hashIndex >= 0 ? searchAndHash.slice(0, hashIndex) : searchAndHash;
    const hashPart = hashIndex >= 0 ? searchAndHash.slice(hashIndex + 1) : "";

    // Validate viz tab — "mds", "freelist", "similarity", "centrality", and "piles" are valid.
    const vizTab = hashPart.toLowerCase();
    if (vizTab !== "mds" && vizTab !== "freelist" && vizTab !== "similarity" && vizTab !== "centrality" && vizTab !== "piles" && vizTab !== "") return null;

    const params = new URLSearchParams(searchPart);
    const domain = params.get("domain");
    const modelsRaw = params.get("models");

    if (!domain || !modelsRaw) return null;
    if (domain.trim() === "") return null;

    // Split the comma-separated models value; filter out empty strings.
    const models = modelsRaw
      .split(",")
      .map((m) => m.trim())
      .filter((m) => m.length > 0);

    if (models.length === 0) return null;

    const resolvedTab =
      vizTab === "freelist" ? "freelist"
      : vizTab === "similarity" ? "similarity"
      : vizTab === "centrality" ? "centrality"
      : vizTab === "piles" ? "piles"
      : "mds";
    return {
      domain,
      models,
      vizTab: resolvedTab as "mds" | "freelist" | "similarity" | "centrality" | "piles",
    };
  } catch {
    return null;
  }
}
