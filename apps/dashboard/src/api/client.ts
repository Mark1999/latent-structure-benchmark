/**
 * LSB Dashboard API client.
 *
 * Fetches precomputed static JSON files from the same origin as the dashboard.
 * No retries — the dashboard is served from the same domain that hosts the JSON
 * (Cloudflare Pages). A fetch failure means a cache miss or a network issue;
 * retrying automatically could mask structural problems.
 *
 * Same-origin only. No credentials, no cross-origin requests.
 * Complies with CSP: connect-src 'self'.
 */

import type { Manifest, DomainResultPublished } from "../data/types";

const BASE_PATH = "/data";

/**
 * Fetch the manifest.json that lists available domains and analysis versions.
 * Must be called at app startup before any domain fetch.
 *
 * @throws {Error} when fetch fails or response is not OK.
 */
export async function fetchManifest(): Promise<Manifest> {
  const url = `${BASE_PATH}/manifest.json`;
  const response = await fetch(url, {
    credentials: "omit",
    cache: "default",
  });

  if (!response.ok) {
    throw new Error(
      `Failed to load manifest: HTTP ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<Manifest>;
}

/**
 * Fetch a domain result JSON file.
 *
 * @param slug - Domain slug (e.g., "family", "holidays").
 * @param version - Optional analysis version. When omitted, fetches the
 *   latest version ({slug}.json). When provided, fetches the pinned version
 *   ({slug}.v{version}.json) for reproducibility / permalink support.
 * @throws {Error} when fetch fails or response is not OK.
 */
export async function fetchDomain(
  slug: string,
  version?: string
): Promise<DomainResultPublished> {
  const filename = version
    ? `${slug}.v${version}.json`
    : `${slug}.json`;

  const url = `${BASE_PATH}/${filename}`;
  const response = await fetch(url, {
    credentials: "omit",
    cache: "default",
  });

  if (!response.ok) {
    throw new Error(
      `Failed to load domain "${slug}"${version ? ` v${version}` : ""}: HTTP ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<DomainResultPublished>;
}
