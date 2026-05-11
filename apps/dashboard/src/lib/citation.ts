/**
 * Citation string builders — pure functions, no side effects.
 *
 * Produces APA, MLA, Chicago, and BibTeX citation strings for LSB domain
 * results. Both the benchmark name ("LSB") and the website name
 * ("Cognitive Structure Lab") appear in every format per ARCHITECTURE.md §1.6
 * binding implication 4.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 * Reference: ARCHITECTURE.md §1.6 — project naming
 */

export interface CitationContext {
  domain: string;          // slug, e.g. "family"
  domainTitle: string;     // title-case, e.g. "Family"
  analysisVersion: string; // e.g. "0.2"
  generatedAt: string;     // ISO-8601, e.g. "2026-05-07T00:07:50.238646Z"
  selectedModels: string[];
  baseUrl?: string;        // default "https://cogstructurelab.com"
}

/** Extract a four-digit year from an ISO-8601 date string. */
function yearFromIso(iso: string): string {
  const m = iso.match(/^(\d{4})/);
  return m ? m[1] : String(new Date().getFullYear());
}

/** Format today's date as "DD Month YYYY" for MLA access dates. */
export function accessDate(): string {
  const d = new Date();
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
}

/**
 * APA citation.
 *
 * Format:
 * Cognitive Structure Lab. (YYYY). LSB: {Domain} domain MDS [Data set].
 * cogstructurelab.com/{domain}
 */
export function buildApa(ctx: CitationContext): string {
  const year = yearFromIso(ctx.generatedAt);
  const base = (ctx.baseUrl ?? "https://cogstructurelab.com").replace(/\/$/, "");
  const url = `${base}/${ctx.domain}`;
  return `Cognitive Structure Lab. (${year}). LSB: ${ctx.domainTitle} domain MDS [Data set]. ${url}`;
}

/**
 * MLA citation.
 *
 * Format:
 * Cognitive Structure Lab. "LSB: {Domain} domain MDS." Cognitive Structure Lab,
 * YYYY, cogstructurelab.com/{domain}. Accessed DD Month YYYY.
 */
export function buildMla(ctx: CitationContext): string {
  const year = yearFromIso(ctx.generatedAt);
  const base = (ctx.baseUrl ?? "https://cogstructurelab.com").replace(/\/$/, "");
  const url = `${base}/${ctx.domain}`;
  return `Cognitive Structure Lab. "LSB: ${ctx.domainTitle} domain MDS." Cognitive Structure Lab, ${year}, ${url}. Accessed ${accessDate()}.`;
}

/**
 * Chicago author-date citation.
 *
 * Format:
 * Cognitive Structure Lab. YYYY. "LSB: {Domain} domain MDS." Cognitive
 * Structure Lab. cogstructurelab.com/{domain}.
 */
export function buildChicago(ctx: CitationContext): string {
  const year = yearFromIso(ctx.generatedAt);
  const base = (ctx.baseUrl ?? "https://cogstructurelab.com").replace(/\/$/, "");
  const url = `${base}/${ctx.domain}`;
  return `Cognitive Structure Lab. ${year}. "LSB: ${ctx.domainTitle} domain MDS." Cognitive Structure Lab. ${url}.`;
}

/**
 * BibTeX citation.
 *
 * Key: lsb_{domain}_{year} — lowercase slug characters only.
 *
 * @misc{lsb_{domain}_{year},
 *   author = {{Cognitive Structure Lab}},
 *   title  = {LSB: {Domain} domain MDS},
 *   year   = {YYYY},
 *   note   = {Analysis version {X}; models: {model_list}},
 *   url    = {https://cogstructurelab.com/{domain}},
 * }
 */
export function buildBibtex(ctx: CitationContext): string {
  const year = yearFromIso(ctx.generatedAt);
  const base = (ctx.baseUrl ?? "https://cogstructurelab.com").replace(/\/$/, "");
  const url = `${base}/${ctx.domain}`;
  // BibTeX key: lowercase slug chars only (replace any non-alnum/hyphen/underscore).
  const key = `lsb_${ctx.domain.toLowerCase().replace(/[^a-z0-9_]/g, "_")}_${year}`;
  const modelList = ctx.selectedModels.join(", ");
  return [
    `@misc{${key},`,
    `  author = {{Cognitive Structure Lab}},`,
    `  title  = {LSB: ${ctx.domainTitle} domain MDS},`,
    `  year   = {${year}},`,
    `  note   = {Analysis version ${ctx.analysisVersion}; models: ${modelList}},`,
    `  url    = {${url}},`,
    `}`,
  ].join("\n");
}
