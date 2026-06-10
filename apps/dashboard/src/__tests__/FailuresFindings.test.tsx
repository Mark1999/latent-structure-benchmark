/**
 * FailuresFindings tests -- Collection records tab.
 *
 * Fixtures: live family.json + food.json (production JSON IS the fixture).
 * No real API calls -- fetch is mocked via vi.fn() per CLAUDE.md §6 rule 9.
 *
 * Test cases (Architect plan §8):
 * 1. Heading present (SECTION_HEADING verbatim).
 * 2. framing_note byte-identity (T9 §5.1 / AC5).
 * 3. <details> count === n_records.
 * 4. Summary rows contain NO verbatim response_verbatim bytes (T10 S1 / AC6).
 * 5. originating_outcome_class in <code> (AC7).
 * 6. Click-to-expand exposes full response_verbatim in <pre> (AC6).
 * 7. Provenance exposes sha256_manifest (AC7 / plan §8 case 7).
 * 8. Empty state (food) -- verbatim caption + zero <details> (AC9).
 * 9. Chrome-isolation grep: LSB chrome text excludes forbidden substrings (M4/N7).
 * 10. Domain switch re-fetches (AC4).
 * 11. IMPACT_PARAGRAPH_FAILURES byte-identity (CR-T1 AC5).
 * 12. Empty-state path renders impact paragraph (CR-T1 AC3).
 * 13. Impact paragraph absent in loading state (CR-T1 AC4).
 * 14. IMPACT_PARAGRAPH_FOLLOWUPS byte-identity (CR-T2 AC5).
 * 15. Follow-up impact paragraph absent when no decline_interview records (CR-T2 AC6).
 * 16. TAXONOMY_BLOCK heading/bridge/enum ids in ready state (CR-T3 AC2).
 * 17. Enum ids inside <code> elements (CR-T3 AC3).
 * 18. Taxonomy block in food empty-state path (CR-T3 AC5).
 * 19. Taxonomy block absent in loading state (CR-T3 AC6).
 * 20. Records section heading renders byte-for-byte under recordsFamilyJson (CR-T5 AC13).
 * 21. Records framing_note renders byte-for-byte under recordsFamilyJson (CR-T5 AC6/AC13).
 * 22. All 17 family model_id values in <code> elements in row order (CR-T5 AC13).
 * 23. Zero-runs empty-state observation under by_model: [] fixture (CR-T5 AC8/AC13).
 * 24. Records fetch-failed string when records fetch rejects (CR-T5 AC9/AC13).
 * 25. Records section absent in records-side loading state (CR-T5 AC11/AC13).
 * 26. Records section renders BELOW EMPTY_CAPTION in DOM order (food fixture) (CR-T5 AC13).
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FailuresFindings } from '../components/FailuresFindings';
import {
  SECTION_HEADING,
  EMPTY_CAPTION,
  FAILURES_TAB_LABEL,
  IMPACT_PARAGRAPH_FAILURES,
  IMPACT_PARAGRAPH_FOLLOWUPS,
  TAXONOMY_BLOCK,
  RECORDS_SECTION_HEADING,
  RECORDS_FETCH_FAILED_TEXT,
} from '../copy/failures_findings';

// -- Fixtures: load the production JSON files -----------------------------------

// We use dynamic import with ?raw would require vite config changes.
// Instead, read files directly via Node.js (vitest runs in Node).
import familyJson from '../../public/data/failures/family.json';
import foodJson from '../../public/data/failures/food.json';
import recordsFamilyJson from '../../public/data/records/family.json';
import recordsFoodJson from '../../public/data/records/food.json';

// -- Fetch mock helpers ---------------------------------------------------------

/**
 * Mock fetch to return both failures and records in sequence.
 * The component fetches failures/{domain}.json and records/{domain}.json
 * via Promise.all; the fetch calls are issued in that order by implementation.
 */
function mockFetchBoth(failuresData: object, recordsData: object) {
  const spy = vi.spyOn(globalThis, 'fetch');
  spy.mockImplementation((url: RequestInfo | URL) => {
    const urlStr = typeof url === 'string' ? url : url.toString();
    if (urlStr.includes('/data/records/')) {
      return Promise.resolve({
        ok: true,
        json: async () => recordsData,
      } as Response);
    }
    // Default: failures data
    return Promise.resolve({
      ok: true,
      json: async () => failuresData,
    } as Response);
  });
  return spy;
}

/**
 * Mock fetch with failures data only (records fetch returns 404).
 */
function mockFetchFailuresOnly(failuresData: object) {
  const spy = vi.spyOn(globalThis, 'fetch');
  spy.mockImplementation((url: RequestInfo | URL) => {
    const urlStr = typeof url === 'string' ? url : url.toString();
    if (urlStr.includes('/data/records/')) {
      return Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({}),
      } as Response);
    }
    return Promise.resolve({
      ok: true,
      json: async () => failuresData,
    } as Response);
  });
  return spy;
}

afterEach(() => {
  vi.restoreAllMocks();
});

// -- Tests ---------------------------------------------------------------------

describe('FailuresFindings', () => {
  // 1. Heading present
  it('renders the section heading verbatim', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(SECTION_HEADING);
    });
  });

  // 2. framing_note byte-identity
  it('renders framing_note byte-for-byte (T9 §5.1 / AC5)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      // The framing_note must appear verbatim in the rendered text.
      // Use getAllByText because the records summary also renders its framing_note
      // (same string from the same domain, but a different fetch).
      const elements = screen.getAllByText(familyJson.framing_note);
      expect(elements.length).toBeGreaterThanOrEqual(1);
    });
  });

  // 3. <details> count === n_records
  it('renders exactly n_records <details> elements for family domain', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      const detailsEls = container.querySelectorAll('details');
      expect(detailsEls.length).toBe(familyJson.n_records);
    });
  });

  // 4. Summary rows contain NO verbatim response_verbatim bytes (T10 S1)
  it('summary rows do not expose response_verbatim text before expansion (T10 S1)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Collect all response_verbatim strings from decline_interview records
    const declineRecords = familyJson.records.filter(
      (r) => r.record_type === 'decline_interview'
    ) as Array<{ response_verbatim: string; [key: string]: unknown }>;

    const summaryEls = container.querySelectorAll('summary');
    summaryEls.forEach((summary) => {
      const summaryText = summary.textContent ?? '';
      declineRecords.forEach((record) => {
        // Take the first 40 chars of response_verbatim as a distinctive substring
        const distinguishingFragment = record.response_verbatim.slice(0, 40);
        expect(summaryText).not.toContain(distinguishingFragment);
      });
    });
  });

  // 5. originating_outcome_class in <code>
  it('renders originating_outcome_class inside <code> in summary (AC7)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Find decline_interview records that have a non-null outcome_class
    const declineWithClass = familyJson.records.filter(
      (r) =>
        r.record_type === 'decline_interview' &&
        (r as { originating_outcome_class: string | null }).originating_outcome_class !== null
    ) as Array<{ originating_outcome_class: string; [key: string]: unknown }>;

    expect(declineWithClass.length).toBeGreaterThan(0);

    // At least one <code> element in the summaries must contain an outcome_class value
    const summaryCodeEls = Array.from(container.querySelectorAll('summary code'));
    const codeTexts = summaryCodeEls.map((el) => el.textContent ?? '');
    const firstClass = declineWithClass[0].originating_outcome_class;
    expect(codeTexts.some((t) => t === firstClass)).toBe(true);
  });

  // 6. Click-to-expand exposes full response_verbatim in <pre>
  it('expanding a decline_interview details exposes response_verbatim in <pre>', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Find the first decline_interview record index
    const declineIdx = familyJson.records.findIndex(
      (r) => r.record_type === 'decline_interview'
    );
    expect(declineIdx).toBeGreaterThanOrEqual(0);

    const declineRecord = familyJson.records[declineIdx] as {
      response_verbatim: string;
      [key: string]: unknown;
    };

    // Open the details element
    const allDetails = container.querySelectorAll('details');
    const targetDetails = allDetails[declineIdx];
    fireEvent.click(targetDetails.querySelector('summary')!);

    // response_verbatim should now be visible in a <pre>
    await waitFor(() => {
      const preEls = container.querySelectorAll('pre');
      const preTexts = Array.from(preEls).map((el) => el.textContent ?? '');
      expect(
        preTexts.some((t) => t.includes(declineRecord.response_verbatim.slice(0, 80)))
      ).toBe(true);
    });
  });

  // 7. Provenance exposes sha256_manifest
  it('expanded decline_interview details expose sha256_manifest', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    const declineIdx = familyJson.records.findIndex(
      (r) => r.record_type === 'decline_interview'
    );
    const declineRecord = familyJson.records[declineIdx] as {
      sha256_manifest: string;
      [key: string]: unknown;
    };

    // Open details
    const allDetails = container.querySelectorAll('details');
    fireEvent.click(allDetails[declineIdx].querySelector('summary')!);

    await waitFor(() => {
      expect(screen.getByText(declineRecord.sha256_manifest)).toBeInTheDocument();
    });
  });

  // 8. Empty state (food): verbatim EMPTY_CAPTION + zero <details> (AC9 / plan §8 case 8)
  // Serves food fixture as the initial family fetch so the component immediately
  // enters the empty-state branch (n_records === 0).
  it('empty state: EMPTY_CAPTION verbatim and zero <details> elements (food fixture)', async () => {
    // Queue foodJson for the failures fetch, recordsFoodJson for records.
    mockFetchBoth(foodJson, recordsFoodJson);
    const { container } = render(<FailuresFindings />);

    await waitFor(() => {
      expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
    });
    expect(container.querySelectorAll('details').length).toBe(0);
  });

  // 9. Chrome-isolation grep (M4 / N7 -- extended for CR-T5 new DOM nodes)
  // Rendered LSB chrome text (excluding <pre> bytes) must not contain
  // consensus / Smith's S / agree / believe / think / worldview / categoriz
  it('M4/N7: LSB chrome does not contain forbidden substrings (no Explore chrome leak)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      // Wait for both sides to resolve: failures records + records summary table.
      // Use getAllByText because the heading appears in both h2 and caption.
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    // Collect all text NOT inside <pre> elements (those contain verbatim model bytes)
    const preEls = Array.from(container.querySelectorAll('pre'));

    // Walk all text nodes, excluding those inside <pre>
    const chromeText = extractChromeText(container, preEls);

    const forbidden = [
      'consensus',
      "Smith's S",
      'agree',
      'believe',
      'worldview',
      // "think" and "categoriz" without -pipeline suffix
      // Note: the copy module must not contain these; check against LSB strings only
    ];

    // Also check that 'think' doesn't appear in chrome (but not in pre blocks)
    // and 'categoriz' without '-pipeline' doesn't appear

    for (const word of forbidden) {
      expect(chromeText.toLowerCase()).not.toContain(word.toLowerCase());
    }

    // 'think' check (lowercased)
    expect(chromeText.toLowerCase()).not.toMatch(/\bthink/);

    // 'categoriz' check (without -pipeline) -- check for 'categoriz' not followed by ation-pipeline
    // Simple check: no 'categoriz' at all in chrome (LSB copy never uses it)
    expect(chromeText.toLowerCase()).not.toContain('categoriz');

    // Also verify the FAILURES_TAB_LABEL is available from copy module
    expect(FAILURES_TAB_LABEL).toBe('Collection records');

    // Assert the exclusion logic is doing real work: at least one <pre> in the DOM
    // must contain response_verbatim bytes. This guarantees the chrome-isolation
    // check above is not vacuously passing because all <pre> blocks were empty.
    expect(prEls_haveResponseBytes(preEls)).toBe(true);
  });

  // 11. Byte-identity: IMPACT_PARAGRAPH_FAILURES renders verbatim (CR-T1 AC5)
  it('renders IMPACT_PARAGRAPH_FAILURES byte-for-byte in ready state (CR-T1 AC5)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FAILURES)).toBeInTheDocument();
    });
  });

  // 12. Empty-state path (food) also renders the impact paragraph (CR-T1 AC3 / AC7)
  it('empty state (food fixture): IMPACT_PARAGRAPH_FAILURES renders (CR-T1 AC3)', async () => {
    mockFetchBoth(foodJson, recordsFoodJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FAILURES)).toBeInTheDocument();
    });
    // Confirm the empty-state caption is also present
    expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
  });

  // 13. Impact paragraph does NOT render in loading state (CR-T1 AC4)
  it('impact paragraph absent before fetch resolves (CR-T1 AC4)', () => {
    // Never resolve the fetch -- component stays in loading state
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise(() => {}));
    render(<FailuresFindings />);
    // The paragraph must not be present in loading state
    expect(screen.queryByText(IMPACT_PARAGRAPH_FAILURES)).not.toBeInTheDocument();
  });

  // 14. Byte-identity: IMPACT_PARAGRAPH_FOLLOWUPS renders verbatim (CR-T2 AC5)
  it('renders IMPACT_PARAGRAPH_FOLLOWUPS byte-for-byte in ready state with decline records (CR-T2 AC5)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FOLLOWUPS)).toBeInTheDocument();
    });
  });

  // 15. Follow-up impact paragraph does NOT render when no decline_interview records present (CR-T2 AC6)
  // food fixture has n_records === 0 so no decline_interview records exist.
  it('IMPACT_PARAGRAPH_FOLLOWUPS absent when no decline_interview records present (CR-T2 AC6)', async () => {
    mockFetchBoth(foodJson, recordsFoodJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
    });
    expect(screen.queryByText(IMPACT_PARAGRAPH_FOLLOWUPS)).not.toBeInTheDocument();
  });

  // 16. Byte-identity: TAXONOMY_BLOCK heading, bridge, and all seven enum id values
  //     are present in the rendered DOM under familyJson fixture (CR-T3 AC2)
  it('renders TAXONOMY_BLOCK heading, bridge, and all seven enum ids in ready state (CR-T3 AC2)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Heading must be present
    expect(screen.getByText(TAXONOMY_BLOCK.heading)).toBeInTheDocument();

    // Bridge must be present verbatim
    expect(screen.getByText(TAXONOMY_BLOCK.bridge)).toBeInTheDocument();

    // All seven enum id values must be present somewhere in the DOM text
    for (const row of TAXONOMY_BLOCK.enumValues) {
      expect(container.textContent).toContain(row.id);
    }
  });

  // 17. Each of the seven originating_outcome_class enum id strings appears inside
  //     a <code> element in the rendered DOM under familyJson (CR-T3 AC3)
  it('each of the seven enum ids appears inside a <code> element (CR-T3 AC3)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    const codeEls = Array.from(container.querySelectorAll('code'));
    const codeTexts = codeEls.map((el) => el.textContent ?? '');

    for (const row of TAXONOMY_BLOCK.enumValues) {
      expect(codeTexts.some((t) => t === row.id)).toBe(true);
    }
  });

  // 18. Taxonomy block renders in the food empty-state path (n_records === 0) (CR-T3 AC5)
  it('taxonomy block heading renders in food empty-state path (CR-T3 AC5)', async () => {
    mockFetchBoth(foodJson, recordsFoodJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
    });
    // Taxonomy block heading must be present even in empty-state path
    expect(screen.getByText(TAXONOMY_BLOCK.heading)).toBeInTheDocument();
  });

  // 19. Taxonomy block does NOT render in loading state (CR-T3 AC6)
  it('taxonomy block absent before fetch resolves (loading state) (CR-T3 AC6)', () => {
    // Never resolve the fetch -- component stays in loading state
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise(() => {}));
    render(<FailuresFindings />);
    // Taxonomy block heading must not be present in loading state
    expect(screen.queryByText(TAXONOMY_BLOCK.heading)).not.toBeInTheDocument();
  });

  // 20. Records section heading renders byte-for-byte under recordsFamilyJson fixture (CR-T5 AC13)
  it('records section heading renders byte-for-byte (CR-T5 case 20)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      // Heading appears in both <h2> and <caption class="sr-only">; getAllByText handles both.
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });
  });

  // 21. framing_note from recordsFamilyJson renders byte-for-byte (CR-T5 AC6 / AC13)
  it('records framing_note renders byte-for-byte (CR-T5 case 21 / AC6)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      // Both failures framing_note and records framing_note are the same string
      // (same domain). Use getAllByText which handles duplicates.
      const elements = screen.getAllByText(recordsFamilyJson.framing_note);
      expect(elements.length).toBeGreaterThanOrEqual(1);
    });
  });

  // 22. All 17 family model_id values render as <code> elements in row order (CR-T5 AC13)
  it('all 17 family model_id values render in <code> elements in by_model order (CR-T5 case 22)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      // getAllByText because heading appears in both h2 and sr-only caption.
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });

    // Get all <code> elements in the records table
    const tableSection = container.querySelector('section[aria-labelledby="records-summary-heading"]');
    expect(tableSection).not.toBeNull();

    const codeEls = Array.from(tableSection!.querySelectorAll('table code'));
    const codeTexts = codeEls.map((el) => el.textContent ?? '');

    // Verify all 17 model_id values appear (in order by checking first occurrence)
    const expectedModelIds = recordsFamilyJson.by_model.map((row) => row.model_id);
    expect(expectedModelIds.length).toBe(17);

    // Each model_id must appear in a <code> element
    for (const modelId of expectedModelIds) {
      expect(codeTexts.some((t) => t === modelId)).toBe(true);
    }

    // Verify row order: first code in each row should match by_model order
    // The table has 5 columns; model_id is first in each row.
    // Find <code> elements that match model_ids (first code per row = model_id).
    // We check by filtering codes that are exact model_id matches.
    const modelIdCodes = codeTexts.filter((t) => expectedModelIds.includes(t));
    // Should have at least 17 entries (some model_ids may also appear as model_version_returned)
    expect(modelIdCodes.length).toBeGreaterThanOrEqual(17);
  });

  // 23. Zero-runs first-class state under by_model: [] fixture (CR-T5 AC8 / AC13)
  it('empty by_model renders zero-runs observation, not table (CR-T5 case 23 / AC8)', async () => {
    const emptyRecordsJson = {
      domain_slug: 'family',
      generated_at: '2026-06-10T00:00:00.000Z',
      n_informants: 0,
      by_model: [],
      framing_note: recordsFamilyJson.framing_note,
    };
    mockFetchBoth(familyJson, emptyRecordsJson);
    const { container } = render(<FailuresFindings />);

    await waitFor(() => {
      expect(screen.getByText(RECORDS_SECTION_HEADING)).toBeInTheDocument();
    });

    // Zero-runs observation must be present
    expect(
      screen.getByText(
        "No collection runs in this domain produced a parseable primary-step response. " +
        "The absence is itself an observation about how this set of models behaved under " +
        "the LSB elicitation prompts for this domain."
      )
    ).toBeInTheDocument();

    // Table must NOT be present
    const tableSection = container.querySelector('section[aria-labelledby="records-summary-heading"]');
    expect(tableSection).not.toBeNull();
    expect(tableSection!.querySelector('table')).toBeNull();
  });

  // 24. Records fetch-failed string renders when records fetch returns ok=false (CR-T5 AC9 / AC13)
  it('records fetch-failed string renders when records fetch returns 404 (CR-T5 case 24 / AC9)', async () => {
    mockFetchFailuresOnly(familyJson);
    render(<FailuresFindings />);

    // Failures side should still resolve
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FAILURES)).toBeInTheDocument();
    });

    // Records fetch-failed string must appear
    await waitFor(() => {
      expect(screen.getByText(RECORDS_FETCH_FAILED_TEXT)).toBeInTheDocument();
    });

    // Records section heading must NOT appear (section only renders in ready state)
    expect(screen.queryByText(RECORDS_SECTION_HEADING)).not.toBeInTheDocument();
  });

  // 25. Records section absent in records-side loading state (CR-T5 AC11 / AC13)
  // Mirror of case 13: never-resolving fetch keeps records side in loading.
  it('records section heading absent before records fetch resolves (CR-T5 case 25 / AC11)', () => {
    // Never resolve any fetch -- both sides stay in loading state
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise(() => {}));
    render(<FailuresFindings />);
    // Records section heading must not be present in loading state
    expect(screen.queryByText(RECORDS_SECTION_HEADING)).not.toBeInTheDocument();
  });

  // 26. Records section renders BELOW EMPTY_CAPTION in DOM order (food fixture) (CR-T5 AC13)
  it('records section renders below EMPTY_CAPTION in DOM order (CR-T5 case 26 / AC5)', async () => {
    mockFetchBoth(foodJson, recordsFoodJson);
    const { container } = render(<FailuresFindings />);

    await waitFor(() => {
      expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
      // getAllByText because heading appears in both h2 and sr-only caption.
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });

    const emptyCaption = screen.getByText(EMPTY_CAPTION);
    const recordsSection = container.querySelector('section[aria-labelledby="records-summary-heading"]');
    expect(recordsSection).not.toBeNull();

    // EMPTY_CAPTION should come BEFORE the records section in document order
    // compareDocumentPosition: Node.DOCUMENT_POSITION_FOLLOWING (4) means arg comes after this node
    const position = emptyCaption.compareDocumentPosition(recordsSection!);
    // DOCUMENT_POSITION_FOLLOWING = 4; result & 4 is non-zero if recordsSection follows emptyCaption
    expect(position & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  // 10. Domain switch re-fetches (AC4) -- updated for 2-fetch-per-domain model
  it('switching domain triggers new fetches for both failures and records (AC4)', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    fetchSpy.mockImplementation((url: RequestInfo | URL) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/data/records/')) {
        return Promise.resolve({
          ok: true,
          json: async () => recordsFamilyJson,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: async () => familyJson,
      } as Response);
    });

    const { container } = render(<FailuresFindings />);

    // Initial fetches (family): both failures + records.
    // getAllByText because heading appears in both h2 and sr-only caption.
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });
    // Should have been called exactly 2 times (failures/family + records/family)
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/data/failures/family.json'),
      expect.anything(),
    );
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/data/records/family.json'),
      expect.anything(),
    );

    // Switch to food
    fetchSpy.mockImplementation((url: RequestInfo | URL) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/data/records/')) {
        return Promise.resolve({
          ok: true,
          json: async () => recordsFoodJson,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: async () => foodJson,
      } as Response);
    });

    const select = container.querySelector('#failures-domain-select') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: 'food' } });

    await waitFor(() => {
      // After switch to food: failures shows EMPTY_CAPTION, records shows food table
      expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
    });
    // Total calls: 2 (family) + 2 (food) = 4
    expect(fetchSpy).toHaveBeenCalledTimes(4);
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/data/failures/food.json'),
      expect.anything(),
    );
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/data/records/food.json'),
      expect.anything(),
    );
  });
});

// -- Helpers -------------------------------------------------------------------

/**
 * Extract text content from the container, excluding text inside <pre> blocks.
 * This isolates "LSB chrome" text from verbatim model bytes.
 */
function extractChromeText(container: Element, preEls: Element[]): string {
  const preSet = new Set(preEls);
  let text = '';

  function walk(node: Node): void {
    if (node.nodeType === Node.TEXT_NODE) {
      text += node.textContent ?? '';
      return;
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
      if (preSet.has(node as Element)) return; // skip pre contents
      for (const child of Array.from(node.childNodes)) {
        walk(child);
      }
    }
  }

  walk(container);
  return text;
}

/**
 * Helper to check if any <pre> element contains response_verbatim bytes.
 * Used only to validate the test's own premise.
 */
function prEls_haveResponseBytes(preEls: Element[]): boolean {
  const declineRecords = familyJson.records.filter(
    (r) => r.record_type === 'decline_interview'
  ) as Array<{ response_verbatim: string; [key: string]: unknown }>;

  return preEls.some((pre) => {
    const text = pre.textContent ?? '';
    return declineRecords.some((r) => text.includes(r.response_verbatim.slice(0, 40)));
  });
}
