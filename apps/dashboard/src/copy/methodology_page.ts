// apps/dashboard/src/copy/methodology_page.ts
//
// Copy module for the /methodology placeholder page (Phase 8 T10.1).
// Placeholder — full copy is pending CDA SME sign-off in T10.3.
// Do not edit the archLinkHref anchor path without updating the test
// assertion in src/__tests__/methodology-page.test.tsx.

/**
 * Page title shown in the <h1> on the /methodology route.
 * WCAG: unique <h1> per route — heading-level contract with MethodologyPagePlaceholder.tsx.
 */
export const pageTitle = "Methodology";

/**
 * Single-sentence placeholder body.
 * "in preparation" — confirmed by UI/UX verdict 2026-05-19. No date commitment.
 */
export const pageBody = "This page is in preparation.";

/**
 * Displayed link text for the ARCHITECTURE.md reference.
 * Points readers to the existing canonical scientific framing doc.
 */
export const archLinkText = "ARCHITECTURE.md §1.5 — Scientific framing and known limitations";

/**
 * GitHub file-root URL for ARCHITECTURE.md in the canonical repo.
 * No heading anchor — per UI/UX verdict 2026-05-19 required-before-merge item 1:
 * heading slugs are fragile; link to file root only.
 * Repo path: Mark1999/latent-structure-benchmark (confirmed by git remote -v).
 */
export const archLinkHref =
  "https://github.com/Mark1999/latent-structure-benchmark/blob/master/ARCHITECTURE.md";
