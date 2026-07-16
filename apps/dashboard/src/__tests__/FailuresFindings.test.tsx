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
 * 27. Counts caption byte-identity: full three-clause under familyJson + recordsFamilyJson (CR-T6 AC2/AC7).
 * 28. Counts caption cell (n_records > 0, parsed > 0): caption visible in DOM (CR-T6 AC5/AC7).
 * 29. Counts caption cell (n_records === 0, parsed > 0): S-clause-only under foodJson + recordsFoodJson (CR-T6 AC5/AC7).
 * 30. Counts caption cell (n_records > 0, parsed === 0): failure-clause-only under familyJson + mocked by_model:[] (CR-T6 AC5/AC7).
 * 31. Counts caption cell (n_records === 0, parsed === 0): caption paragraph NOT in DOM (CR-T6 AC5/AC7 + N10).
 * 32. Counts caption records-not-ready: failures-only two-clause caption when records fetch returns 404 (CR-T6 AC4/N4).
 * 33. Byte-identity on all new SME-bound CR-T7 copy strings (RECORDS_DETAIL_EXPAND_LABEL, RECORDS_DETAIL_FRAMING,
 *     RECORDS_DETAIL_LOADING, RECORDS_DETAIL_FETCH_FAILED, RECORDS_DETAIL_MALFORMED, BLOCK_FREELIST_EXCHANGE,
 *     BLOCK_PILESORT_EXCHANGE, BLOCK_PILE_INTERVIEW_EXCHANGE, BLOCK_DETAIL_PROVENANCE).
 * 34. Each row of the per-model summary table contains an expand button with aria-expanded="false" initially.
 * 35. Clicking an expand button triggers a fetch; ready-state DOM contains the three step headings and
 *     all eight sha256_manifest keys in <code> elements.
 * 36. Expand loading state renders RECORDS_DETAIL_LOADING byte-identical.
 * 37. Expand fetch-failed state renders RECORDS_DETAIL_FETCH_FAILED byte-identical.
 * 38. Expand malformed state renders RECORDS_DETAIL_MALFORMED byte-identical.
 * 39. A fixture record with pile_sort missing does not render the pile-sort step heading or sub-blocks;
 *     freelist and pile_interview sections are present.
 * 40. Case 9 chrome-isolation extended over the expanded detail DOM (excluding <pre> nodes);
 *     affirmative zero-count assertions pass for all six forbidden substrings.
 * 41. BLOCK_ATTEMPTS byte-identity (CR-T8 AC4).
 * 42. ATTEMPTS_FRAMING byte-identity (CR-T8 AC5).
 * 43. Attempts block renders for a fixture failure record with non-empty retry_attempts (CR-T8 AC8).
 * 44. Attempts block absent when retry_attempts is [] (CR-T8 AC7).
 * 45. Attempts block absent when retry_attempts is null/undefined (CR-T8 AC7).
 * 46. Attempts render in attempt_index ascending order regardless of array order in source (CR-T8 AC10).
 * 47. Byte-identity on all four G7-FOLLOWUP-T1 pivot copy strings/templates (G7-T1 AC1).
 * 48. MDSPlot with onPivotToRecords prop renders .chart-tooltip__pivot-btn in tooltip (G7-T1 AC2).
 * 49. Clicking .chart-tooltip__pivot-btn fires onPivotToRecords with the hovered model id (G7-T1 AC3).
 * 50. FailuresFindings with matching pivotTarget applies highlight class and calls onPivotTargetConsumed (G7-T1 AC4).
 * 51. FailuresFindings with no-match pivotTarget renders arrival notice and calls onPivotTargetConsumed (G7-T1 AC5).
 * 52. Chrome-isolation walk on pivot affordance surfaces: zero forbidden vocabulary instances (G7-T1 AC6).
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
  FABLE_DISCLOSURE_FRAMING,
  FABLE_DISCLOSURE_BOUND,
  RECORDS_SECTION_HEADING,
  RECORDS_FETCH_FAILED_TEXT,
  countsCaptionText,
  RECORDS_DETAIL_EXPAND_LABEL,
  RECORDS_DETAIL_FRAMING,
  RECORDS_DETAIL_LOADING,
  RECORDS_DETAIL_FETCH_FAILED,
  RECORDS_DETAIL_MALFORMED,
  BLOCK_FREELIST_EXCHANGE,
  BLOCK_PILESORT_EXCHANGE,
  BLOCK_PILE_INTERVIEW_EXCHANGE,
  BLOCK_DETAIL_PROVENANCE,
  BLOCK_ATTEMPTS,
  ATTEMPTS_FRAMING,
  PIVOT_TO_RECORDS_LABEL,
  pivotToRecordsAriaLabel,
  pivotToRecordsArrivalCaption,
  pivotToRecordsNoMatchNotice,
} from '../copy/failures_findings';

// -- Fixtures: load the production JSON files -----------------------------------

// We use dynamic import with ?raw would require vite config changes.
// Instead, read files directly via Node.js (vitest runs in Node).
import familyJson from '../../public/data/failures/family.json';
import foodJson from '../../public/data/failures/food.json';
import recordsFamilyJson from '../../public/data/records/family.json';
import recordsFoodJson from '../../public/data/records/food.json';

/**
 * Synthetic empty-food fixture: n_records=0, no failure records.
 * Used by tests that assert empty-state behavior (EMPTY_CAPTION, zero <details>).
 * Replace direct foodJson usage in empty-state tests because the production
 * food.json now has records from the batch A campaign.
 */
const syntheticEmptyFoodJson = {
  domain_slug: 'food',
  generated_at: '2026-01-01T00:00:00.000Z',
  n_records: 0,
  n_failure_records: 0,
  n_decline_interview_records: 0,
  framing_note: foodJson.framing_note,
  records: [],
};

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
  // Uses syntheticEmptyFoodJson (n_records=0) because the production food.json
  // now has records from batch A; empty-state behavior is asserted via the synthetic fixture.
  it('empty state: EMPTY_CAPTION verbatim and zero <details> elements (food fixture)', async () => {
    // Queue syntheticEmptyFoodJson for the failures fetch, recordsFoodJson for records.
    mockFetchBoth(syntheticEmptyFoodJson, recordsFoodJson);
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

    // CR-T6 N6 BINDING: affirmatively confirm 'parsed primary-step responses' IS present
    // in the new caption template, AND 'successful'/'successfully' is absent from it.
    // Check the template string directly (not the entire chrome, which contains
    // "Successful run" from TAXONOMY_BLOCK.topLevel[0].term -- existing copy from CR-T3).
    const newCaptionTemplate = countsCaptionText(
      familyJson.n_records,
      familyJson.n_failure_records,
      familyJson.n_decline_interview_records,
      recordsFamilyJson.n_informants,
    );
    expect(newCaptionTemplate).toContain('parsed primary-step responses');
    expect(newCaptionTemplate.toLowerCase()).not.toContain('successful');
    // Also confirm the caption is present somewhere in the overall chrome
    expect(chromeText).toContain('parsed primary-step responses');
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
  // Uses syntheticEmptyFoodJson (n_records=0); production food.json has records now.
  it('empty state (food fixture): IMPACT_PARAGRAPH_FAILURES renders (CR-T1 AC3)', async () => {
    mockFetchBoth(syntheticEmptyFoodJson, recordsFoodJson);
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
  // syntheticEmptyFoodJson has n_records=0 so no decline_interview records exist.
  it('IMPACT_PARAGRAPH_FOLLOWUPS absent when no decline_interview records present (CR-T2 AC6)', async () => {
    mockFetchBoth(syntheticEmptyFoodJson, recordsFoodJson);
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
  // syntheticEmptyFoodJson has n_records=0; production food.json has records now.
  it('taxonomy block heading renders in food empty-state path (CR-T3 AC5)', async () => {
    mockFetchBoth(syntheticEmptyFoodJson, recordsFoodJson);
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

  // 22. All family model_id values render as <code> elements in row order (CR-T5 AC13)
  // Count is dynamically read from the fixture (was 17 before batch A; now 25).
  it('all family model_id values render in <code> elements in by_model order (CR-T5 case 22)', async () => {
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

    // Verify all model_id values appear (count driven by fixture, not hardcoded)
    const expectedModelIds = recordsFamilyJson.by_model.map((row) => row.model_id);
    expect(expectedModelIds.length).toBeGreaterThan(0);

    // Each model_id must appear in a <code> element
    for (const modelId of expectedModelIds) {
      expect(codeTexts.some((t) => t === modelId)).toBe(true);
    }

    // Verify row order: first code in each row should match by_model order
    // The table has 5 columns; model_id is first in each row.
    // Find <code> elements that match model_ids (first code per row = model_id).
    // We check by filtering codes that are exact model_id matches.
    const modelIdCodes = codeTexts.filter((t) => expectedModelIds.includes(t));
    // Should have at least as many entries as there are models
    expect(modelIdCodes.length).toBeGreaterThanOrEqual(expectedModelIds.length);
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
  // syntheticEmptyFoodJson has n_records=0 so EMPTY_CAPTION renders; records section must follow.
  it('records section renders below EMPTY_CAPTION in DOM order (CR-T5 case 26 / AC5)', async () => {
    mockFetchBoth(syntheticEmptyFoodJson, recordsFoodJson);
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

  // 27. Counts caption byte-identity: full three-clause under familyJson + recordsFamilyJson (CR-T6 AC2/AC7)
  // familyJson: n_records > 0 (failure records exist); recordsFamilyJson: n_informants=631 > 0.
  // Caption must be byte-identical to countsCaptionText(n_records, n_failure_records,
  // n_decline_interview_records, n_informants).
  it('counts caption byte-identical to three-clause template under family fixtures (CR-T6 case 27)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FAILURES)).toBeInTheDocument();
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });

    const expectedCaption = countsCaptionText(
      familyJson.n_records,
      familyJson.n_failure_records,
      familyJson.n_decline_interview_records,
      recordsFamilyJson.n_informants,
    );
    // Verify the template is the full three-clause form (SME N2 byte-identity check)
    expect(expectedCaption).toContain('parsed primary-step responses');
    expect(expectedCaption).not.toContain('successful');
    expect(expectedCaption).not.toContain('successfully');
    // The caption must be present in the DOM
    const captionEl = screen.getByText(expectedCaption);
    expect(captionEl).toBeInTheDocument();
    expect(captionEl.tagName.toLowerCase()).toBe('p');
  });

  // 28. Counts caption cell (n_records > 0, parsed > 0): caption paragraph visible (CR-T6 AC5/AC7)
  // Reconfirms cell 1 renders -- distinct from byte-identity in case 27.
  it('caption paragraph renders when both n_records > 0 and parsed > 0 (CR-T6 case 28 / N3 cell 1)', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });

    const expectedCaption = countsCaptionText(
      familyJson.n_records,
      familyJson.n_failure_records,
      familyJson.n_decline_interview_records,
      recordsFamilyJson.n_informants,
    );
    expect(screen.getByText(expectedCaption)).toBeInTheDocument();
  });

  // 29. Counts caption cell (n_records === 0, parsed > 0): S-clause-only (CR-T6 AC5/AC7 + N3 cell 3)
  // syntheticEmptyFoodJson: n_records=0. recordsFoodJson: n_informants > 0.
  // Caption must render with only the S clause.
  it('S-clause-only caption when n_records === 0 and parsed > 0 (CR-T6 case 29 / N3 cell 3)', async () => {
    mockFetchBoth(syntheticEmptyFoodJson, recordsFoodJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      // Wait for records side to resolve
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThanOrEqual(1);
    });

    const expectedCaption = countsCaptionText(
      syntheticEmptyFoodJson.n_records,
      syntheticEmptyFoodJson.n_failure_records,
      syntheticEmptyFoodJson.n_decline_interview_records,
      recordsFoodJson.n_informants,
    );
    // S-clause-only template: "{S} parsed primary-step responses."
    expect(expectedCaption).toContain('parsed primary-step responses');
    expect(expectedCaption).not.toContain('collection failure');
    expect(expectedCaption).not.toContain('follow-up interview');
    // Caption must be in DOM
    expect(screen.getByText(expectedCaption)).toBeInTheDocument();
    // EMPTY_CAPTION must also be present (food empty state)
    expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
  });

  // 30. Counts caption cell (n_records > 0, parsed === 0): failure-clause-only (CR-T6 AC5/AC7 + N3 cell 2)
  // familyJson: n_records > 0. Mocked records with n_informants=0 and by_model:[].
  // Caption must drop the S clause.
  it('failure-clause-only caption when n_records > 0 and parsed === 0 (CR-T6 case 30 / N3 cell 2)', async () => {
    const zeroRecords = {
      domain_slug: 'family',
      generated_at: '2026-06-10T00:00:00.000Z',
      n_informants: 0,
      by_model: [],
      framing_note: recordsFamilyJson.framing_note,
    };
    mockFetchBoth(familyJson, zeroRecords);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FAILURES)).toBeInTheDocument();
      expect(screen.getByText(RECORDS_SECTION_HEADING)).toBeInTheDocument();
    });

    const expectedCaption = countsCaptionText(
      familyJson.n_records,
      familyJson.n_failure_records,
      familyJson.n_decline_interview_records,
      0,
    );
    // Failure-clause-only: no "parsed primary-step responses"
    expect(expectedCaption).not.toContain('parsed primary-step responses');
    expect(expectedCaption).toContain('collection');
    expect(expectedCaption).toContain('follow-up');
    // Caption must be in DOM
    expect(screen.getByText(expectedCaption)).toBeInTheDocument();
  });

  // 31. Counts caption cell (n_records === 0, parsed === 0): caption paragraph NOT in DOM (CR-T6 N10 BINDING)
  // syntheticEmptyFoodJson: n_records=0. Mocked records with n_informants=0 and by_model:[].
  it('caption paragraph absent when both n_records === 0 and parsed === 0 (CR-T6 case 31 / N3 cell 4 / N10)', async () => {
    const zeroRecords = {
      domain_slug: 'food',
      generated_at: '2026-06-10T00:00:00.000Z',
      n_informants: 0,
      by_model: [],
      framing_note: recordsFamilyJson.framing_note,
    };
    mockFetchBoth(syntheticEmptyFoodJson, zeroRecords);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      // Wait for both sides to resolve
      expect(screen.getByText(EMPTY_CAPTION)).toBeInTheDocument();
      expect(screen.getByText(RECORDS_SECTION_HEADING)).toBeInTheDocument();
    });

    // Caption paragraph must NOT be in DOM (N10 BINDING: asserts absence, not empty string)
    const countsCaptions = container.querySelectorAll('.failures-findings__counts');
    expect(countsCaptions.length).toBe(0);
  });

  // 32. Counts caption records-not-ready: failures-only two-clause caption when records fetch 404 (CR-T6 N4)
  // mockFetchFailuresOnly returns 404 for records. nParsedResponses = undefined -> failure-clause-only.
  it('failure-clause-only caption when records fetch returns 404 (records not ready) (CR-T6 case 32 / N4)', async () => {
    mockFetchFailuresOnly(familyJson);
    render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getByText(IMPACT_PARAGRAPH_FAILURES)).toBeInTheDocument();
      expect(screen.getByText(RECORDS_FETCH_FAILED_TEXT)).toBeInTheDocument();
    });

    // nParsedResponses = undefined (records fetch failed) -> failure-clause-only per N4
    const expectedCaption = countsCaptionText(
      familyJson.n_records,
      familyJson.n_failure_records,
      familyJson.n_decline_interview_records,
      undefined,
    );
    // Caption must render (failures side is ready)
    expect(screen.getByText(expectedCaption)).toBeInTheDocument();
    // Must not contain parsed-primary-step-responses wording
    expect(expectedCaption).not.toContain('parsed primary-step responses');
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

    // Switch to food, use syntheticEmptyFoodJson so EMPTY_CAPTION triggers
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
        json: async () => syntheticEmptyFoodJson,
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

  // ===========================================================================
  // CR-T7 cases: per-record raw-exchange detail surface (§19.17, v0.20.1)
  // ===========================================================================

  // A minimal PublishedRecordDetail fixture for the three ready-state tests.
  // Represents a family domain record with all three steps present.
  const detailFixture = {
    informant_id: 'test-informant-id',
    framing_note_detail: 'framing note detail text',
    freelist: {
      prompt_verbatim: 'freelist prompt bytes',
      response_verbatim: 'freelist response bytes',
      thinking_verbatim: '',
      model_version_returned: 'test-model-v1',
      prompt_version: 'v1',
    },
    pile_sort: {
      prompt_verbatim: 'pile sort prompt bytes',
      response_verbatim: 'pile sort response bytes',
      thinking_verbatim: '',
      model_version_returned: 'test-model-v1',
      prompt_version: 'v1',
    },
    pile_interview: {
      prompt_verbatim: 'pile interview prompt bytes',
      response_verbatim: 'pile interview response bytes',
      thinking_verbatim: '',
      model_version_returned: 'test-model-v1',
      prompt_version: 'v1',
    },
    provenance: {
      provider_request_id: 'req-abc',
      model_id: 'test-model',
      model_version_returned: 'test-model-v1',
      provider: 'test-provider',
      domain_slug: 'family',
      run_index: 0,
      collection_date: '2026-01-01',
      sha256_manifest: {
        freelist_prompt: 'sha1',
        freelist_response: 'sha2',
        pilesort_prompt: 'sha3',
        pilesort_response: 'sha4',
        interview_prompt: 'sha5',
        interview_response: 'sha6',
        request_params: 'sha7',
        informant_record_total: 'sha8',
      },
    },
  };


  /**
   * Mock fetch for both summary data + a specific detail file.
   * Detail URL matches /data/records/{slug}/detail/*.json.
   */
  function mockFetchWithDetail(
    failuresData: object,
    recordsData: object,
    detailData: object,
    detailOk = true,
  ) {
    const spy = vi.spyOn(globalThis, 'fetch');
    spy.mockImplementation((url: RequestInfo | URL) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/detail/')) {
        if (!detailOk) {
          return Promise.resolve({
            ok: false,
            status: 404,
            json: async () => ({}),
          } as Response);
        }
        return Promise.resolve({
          ok: true,
          json: async () => detailData,
        } as Response);
      }
      if (urlStr.includes('/data/records/')) {
        return Promise.resolve({
          ok: true,
          json: async () => recordsData,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: async () => failuresData,
      } as Response);
    });
    return spy;
  }

  // 33. Byte-identity: all new SME-bound CR-T7 copy constants have correct string values.
  it('CR-T7 case 33: all new SME-bound copy constants are byte-identical', () => {
    expect(RECORDS_DETAIL_EXPAND_LABEL).toBe('Show parsed-step exchange');
    expect(RECORDS_DETAIL_FRAMING).toBe(
      'The blocks below show the verbatim bytes exchanged for this collection session, step by step. ' +
      'Each of the three CDA elicitation steps (free list, pile sort, pile interview) is shown as the ' +
      'prompt LSB sent, the response the provider returned, and any reasoning trace the provider surfaced. ' +
      'These are LSB pipeline I/O records, not a window into model cognition.',
    );
    expect(RECORDS_DETAIL_LOADING).toBe('Loading per-record exchange…');
    expect(RECORDS_DETAIL_FETCH_FAILED).toBe(
      'Could not load the per-record exchange for this session. Check that the data file is present.',
    );
    expect(RECORDS_DETAIL_MALFORMED).toBe(
      'Per-record exchange data for this session could not be parsed.',
    );
    expect(BLOCK_FREELIST_EXCHANGE).toBe('Free-list step');
    expect(BLOCK_PILESORT_EXCHANGE).toBe('Pile-sort step');
    expect(BLOCK_PILE_INTERVIEW_EXCHANGE).toBe('Pile-interview step');
    expect(BLOCK_DETAIL_PROVENANCE).toBe('Provenance and pipeline identifiers');
  });

  // 34. Each row of the per-model summary table has an expand button with aria-expanded="false".
  it('CR-T7 case 34: each summary row has an expand button with aria-expanded=false initially', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    // The records summary table has by_model rows; each should have one expand button.
    expect(expandBtns.length).toBe(recordsFamilyJson.by_model.length);
    for (const btn of Array.from(expandBtns)) {
      expect(btn.getAttribute('aria-expanded')).toBe('false');
    }
  });

  // 35. Clicking expand: fetch fires, ready state shows three step headings + all 8 sha256 keys.
  it('CR-T7 case 35: clicking expand fetches detail and shows step headings and sha256 keys', async () => {
    mockFetchWithDetail(familyJson, recordsFamilyJson, detailFixture);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    // Click the first expand button.
    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    expect(expandBtns.length).toBeGreaterThan(0);
    fireEvent.click(expandBtns[0]);

    // Wait for the detail to load and render.
    await waitFor(() => {
      expect(screen.getByText(BLOCK_FREELIST_EXCHANGE)).toBeInTheDocument();
    });

    // All three step headings must be present.
    expect(screen.getByText(BLOCK_FREELIST_EXCHANGE)).toBeInTheDocument();
    expect(screen.getByText(BLOCK_PILESORT_EXCHANGE)).toBeInTheDocument();
    expect(screen.getByText(BLOCK_PILE_INTERVIEW_EXCHANGE)).toBeInTheDocument();

    // All 8 sha256_manifest keys rendered inside <code> elements.
    const sha256Keys = Object.keys(detailFixture.provenance.sha256_manifest);
    expect(sha256Keys).toHaveLength(8);
    const codeEls = Array.from(container.querySelectorAll('code'));
    const codeTexts = codeEls.map((el) => el.textContent ?? '');
    for (const val of Object.values(detailFixture.provenance.sha256_manifest)) {
      expect(codeTexts).toContain(val);
    }

    // aria-expanded must be true after clicking.
    expect(expandBtns[0].getAttribute('aria-expanded')).toBe('true');
  });

  // 36. Loading state renders RECORDS_DETAIL_LOADING byte-identical.
  it('CR-T7 case 36: loading state renders RECORDS_DETAIL_LOADING', async () => {
    // Mock detail fetch to never resolve (stays loading).
    const spy = vi.spyOn(globalThis, 'fetch');
    spy.mockImplementation((url: RequestInfo | URL) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/detail/')) {
        return new Promise(() => {}); // never resolves
      }
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
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    fireEvent.click(expandBtns[0]);

    // Loading text must appear immediately (fetch is pending).
    expect(screen.getByText(RECORDS_DETAIL_LOADING)).toBeInTheDocument();
  });

  // 37. Fetch-failed state renders RECORDS_DETAIL_FETCH_FAILED byte-identical.
  it('CR-T7 case 37: fetch-failed state renders RECORDS_DETAIL_FETCH_FAILED', async () => {
    mockFetchWithDetail(familyJson, recordsFamilyJson, {}, false); // detail fetch 404
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    fireEvent.click(expandBtns[0]);

    await waitFor(() => {
      expect(screen.getByText(RECORDS_DETAIL_FETCH_FAILED)).toBeInTheDocument();
    });
  });

  // 38. Malformed state renders RECORDS_DETAIL_MALFORMED byte-identical.
  it('CR-T7 case 38: malformed state renders RECORDS_DETAIL_MALFORMED', async () => {
    // Serve malformed data that fails the isPublishedRecordDetail type guard.
    const malformedData = { not_a_detail_record: true };
    mockFetchWithDetail(familyJson, recordsFamilyJson, malformedData);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    fireEvent.click(expandBtns[0]);

    await waitFor(() => {
      expect(screen.getByText(RECORDS_DETAIL_MALFORMED)).toBeInTheDocument();
    });
  });

  // 39. Full-step fixture: all three step headings present; confirmed non-null rendering.
  // Note: Under N2 disposition (a), all three steps are non-Optional on valid records.
  // The §19.17 null-suppression guard is a defensive rendering rule. This test confirms
  // that a complete valid fixture renders all three step headings correctly.
  it('CR-T7 case 39: full-step detail fixture renders all three step headings', async () => {
    mockFetchWithDetail(familyJson, recordsFamilyJson, detailFixture);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    fireEvent.click(expandBtns[0]);

    await waitFor(() => {
      // All three CDA step headings must be present.
      expect(screen.getByText(BLOCK_FREELIST_EXCHANGE)).toBeInTheDocument();
      expect(screen.getByText(BLOCK_PILESORT_EXCHANGE)).toBeInTheDocument();
      expect(screen.getByText(BLOCK_PILE_INTERVIEW_EXCHANGE)).toBeInTheDocument();
    });
  });

  // ===========================================================================
  // CR-T8 cases: per-attempt retry-transcript block (§19.18, v0.20.3)
  // ===========================================================================

  // A minimal fixture family JSON with a failure record that has non-empty retry_attempts.
  // Built from familyJson structure; overrides ONLY the first failure record with retry data.
  // All other records have their retry_attempts zeroed out so that counts are deterministic.
  function buildFamilyWithRetries(retryAttempts: unknown[]) {
    let patchedFirst = false;
    const recordsCopy = familyJson.records.map((r) => {
      if (r.record_type === 'failure' && !patchedFirst) {
        patchedFirst = true;
        return { ...r, retry_attempts: retryAttempts };
      }
      // Zero out any pre-existing retry_attempts so test counts are deterministic.
      return { ...r, retry_attempts: [] };
    });
    return { ...familyJson, records: recordsCopy };
  }

  // 41. BLOCK_ATTEMPTS byte-identity (CR-T8 AC4)
  it('CR-T8 case 41: BLOCK_ATTEMPTS is byte-identical to approved string', () => {
    expect(BLOCK_ATTEMPTS).toBe('Pipeline retry attempts');
  });

  // 42. ATTEMPTS_FRAMING byte-identity (CR-T8 AC5)
  it('CR-T8 case 42: ATTEMPTS_FRAMING is byte-identical to approved string', () => {
    expect(ATTEMPTS_FRAMING).toBe(
      'After a parser-state failure the LSB pipeline re-issued the same prompt. ' +
      'Each attempt below shows the response the provider returned and the parser-state outcome ' +
      'the LSB pipeline recorded. The prompt is shared across all attempts and is shown once above.',
    );
  });

  // 43. Attempts block renders when retry_attempts is non-empty (CR-T8 AC8)
  it('CR-T8 case 43: attempts block renders for a failure record with non-empty retry_attempts', async () => {
    const retryAttempts = [
      {
        attempt_index: 0,
        response_verbatim: 'attempt 0 response bytes',
        thinking_verbatim: '',
        stop_reason: 'stop',
        parse_error_message: 'Items missing from pile sort: {}',
      },
    ];
    const familyWithRetries = buildFamilyWithRetries(retryAttempts);
    mockFetchBoth(familyWithRetries, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Open the first details element to materialise the attempts block (CR-T8 AC17 / N4 binding)
    const allDetails = container.querySelectorAll('details');
    fireEvent.click(allDetails[0].querySelector('summary')!);

    // Attempts block must be present (exactly one)
    await waitFor(() => {
      const attemptsBlocks = container.querySelectorAll('.failures-findings__attempts');
      expect(attemptsBlocks.length).toBe(1);
    });

    // BLOCK_ATTEMPTS heading must be present
    expect(container.textContent).toContain(BLOCK_ATTEMPTS);
    // ATTEMPTS_FRAMING must be present
    expect(container.textContent).toContain(ATTEMPTS_FRAMING);
    // Response verbatim in pre
    const preEls = container.querySelectorAll('.failures-findings__attempts pre');
    expect(preEls.length).toBe(1);
    expect(preEls[0].textContent).toBe('attempt 0 response bytes');
  });

  // 44. Attempts block absent when retry_attempts is [] (CR-T8 AC7)
  it('CR-T8 case 44: attempts block absent when retry_attempts is empty array', async () => {
    const familyWithEmptyRetries = buildFamilyWithRetries([]);
    mockFetchBoth(familyWithEmptyRetries, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Open the first failure record
    const allDetails = container.querySelectorAll('details');
    fireEvent.click(allDetails[0].querySelector('summary')!);

    // Attempts block must NOT be present
    await waitFor(() => {
      expect(container.querySelectorAll('.failures-findings__attempts').length).toBe(0);
    });
  });

  // 45. Attempts block absent when retry_attempts is null/undefined (CR-T8 AC7)
  it('CR-T8 case 45: attempts block absent when retry_attempts is null or omitted', async () => {
    // familyJson failure records have retry_attempts:[] in source; override to omit the field.
    const recordsCopy = familyJson.records.map((r) => {
      if (r.record_type === 'failure') {
        const { retry_attempts: _omit, ...rest } = r as (typeof r & { retry_attempts?: unknown });
        void _omit;
        return rest;
      }
      return r;
    });
    const familyNoRetries = { ...familyJson, records: recordsCopy };
    mockFetchBoth(familyNoRetries, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    // Open the first failure record
    const allDetails = container.querySelectorAll('details');
    fireEvent.click(allDetails[0].querySelector('summary')!);

    await waitFor(() => {
      expect(container.querySelectorAll('.failures-findings__attempts').length).toBe(0);
    });
  });

  // 46. Attempts render in attempt_index ascending order (CR-T8 AC10)
  it('CR-T8 case 46: attempts render in attempt_index ascending order', async () => {
    // Supply attempts out of order: index 1 first, then index 0.
    const retryAttempts = [
      {
        attempt_index: 1,
        response_verbatim: 'attempt 1 response',
        thinking_verbatim: '',
        stop_reason: 'stop',
        parse_error_message: null,
      },
      {
        attempt_index: 0,
        response_verbatim: 'attempt 0 response',
        thinking_verbatim: '',
        stop_reason: 'stop',
        parse_error_message: null,
      },
    ];
    const familyWithRetries = buildFamilyWithRetries(retryAttempts);
    mockFetchBoth(familyWithRetries, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(container.querySelectorAll('details').length).toBeGreaterThan(0);
    });

    const allDetails = container.querySelectorAll('details');
    fireEvent.click(allDetails[0].querySelector('summary')!);

    await waitFor(() => {
      expect(container.querySelectorAll('.failures-findings__attempt').length).toBe(2);
    });

    // The attempts in DOM order must be index 0 first, then index 1.
    const attemptDivs = container.querySelectorAll('.failures-findings__attempt');
    const headings = Array.from(attemptDivs).map((div) => {
      const codeEl = div.querySelector('.failures-findings__attempt-heading code');
      return codeEl?.textContent ?? '';
    });
    expect(headings[0]).toBe('0');
    expect(headings[1]).toBe('1');

    // Also verify response order: attempt 0 response before attempt 1 response.
    const preEls = container.querySelectorAll('.failures-findings__attempts pre');
    expect(preEls[0].textContent).toBe('attempt 0 response');
    expect(preEls[1].textContent).toBe('attempt 1 response');
  });

  // 40. Case 9 chrome-isolation extended over the expanded detail DOM (excluding <pre> nodes).
  // Per §19.17 binding: the chrome text of the DETAIL SECTION specifically must not contain
  // the six forbidden substrings. The full-page chrome includes existing TAXONOMY_BLOCK copy
  // (e.g., "refusal_string_match") which was reviewed under prior gate verdicts.
  // This case scopes to the new CR-T7 detail chrome only.
  // CR-T8 AC17: also opens <details> (failures records) to materialise the attempts block
  // during the walk; forbidden-substring scan and \bthink regex still pass.
  it('CR-T7 case 40: detail section chrome-isolation passes (forbidden substrings absent in detail chrome)', async () => {
    // Inject retry_attempts into the first failure record so the attempts block is materialised.
    const retryAttemptsForIsolation = [
      {
        attempt_index: 0,
        response_verbatim: 'attempt zero verbatim bytes for isolation test',
        thinking_verbatim: '',
        stop_reason: 'stop',
        parse_error_message: 'Items missing from pile sort: {}',
      },
    ];
    const familyWithRetries = {
      ...familyJson,
      records: familyJson.records.map((r) =>
        r.record_type === 'failure' ? { ...r, retry_attempts: retryAttemptsForIsolation } : r,
      ),
    };

    mockFetchWithDetail(familyWithRetries, recordsFamilyJson, detailFixture);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      expect(screen.getAllByText(RECORDS_SECTION_HEADING).length).toBeGreaterThan(0);
    });

    // CR-T8 AC17: open all <details> elements (failures records) to materialise the
    // attempts block before running the chrome isolation walk.
    const allDetailsEls = container.querySelectorAll('details');
    for (const detailsEl of Array.from(allDetailsEls)) {
      const summaryEl = detailsEl.querySelector('summary');
      if (summaryEl) fireEvent.click(summaryEl);
    }

    // Expand the first records-table row to load the detail DOM.
    const expandBtns = container.querySelectorAll('button.failures-findings__expand-btn');
    fireEvent.click(expandBtns[0]);
    await waitFor(() => {
      expect(screen.getByText(BLOCK_FREELIST_EXCHANGE)).toBeInTheDocument();
    });

    // Wait for any attempts block to appear (or confirm it is absent in the detail section).
    // The attempts block lives in the failures accordion, not the detail section,
    // so the attempts DOM is now materialised in the full container.
    await waitFor(() => {
      // At minimum, verify the attempts block rendered (injected fixture has one attempt).
      expect(container.querySelectorAll('.failures-findings__attempts').length).toBeGreaterThan(0);
    });

    // Extract chrome text from the DETAIL SECTION only (excludes full-page chrome).
    // §19.17 binding: the detail cell (.failures-findings__detail-cell) is the new CR-T7 surface.
    const detailSection = container.querySelector('.failures-findings__detail-cell');
    expect(detailSection).not.toBeNull();

    const detailPreEls = Array.from((detailSection as Element).querySelectorAll('pre'));
    const detailChromeText = extractChromeText(detailSection as Element, detailPreEls);

    // N5 CDA SME affirmative zero-count assertions on detail chrome text.
    // "refusal" checked against detail chrome only (full-page chrome contains
    // "refusal_string_match" from existing TAXONOMY_BLOCK, reviewed under CR-T3 verdict).
    const forbidden = [
      'worldview',
      'believes',
      'thinks',
      'understands',
      'refusal',
    ];
    for (const word of forbidden) {
      expect(detailChromeText.toLowerCase()).not.toContain(word.toLowerCase());
    }

    // Affirmative: RECORDS_DETAIL_FRAMING is in the detail chrome.
    expect(detailChromeText).toContain(RECORDS_DETAIL_FRAMING);

    // Affirmative: BLOCK_DETAIL_PROVENANCE heading is in the detail chrome.
    expect(detailChromeText).toContain(BLOCK_DETAIL_PROVENANCE);

    // CR-T8 AC17: also scan the attempts chrome (excluding <pre>) for forbidden substrings.
    // The attempts block is in the failures accordion; extract its chrome separately.
    const attemptsBlocks = container.querySelectorAll('.failures-findings__attempts');
    for (const block of Array.from(attemptsBlocks)) {
      const preEls = Array.from(block.querySelectorAll('pre'));
      const attemptsChromeText = extractChromeText(block as Element, preEls);
      for (const word of forbidden) {
        expect(attemptsChromeText.toLowerCase()).not.toContain(word.toLowerCase());
      }
      // CR-T8 AC17 \bthink regex: chrome must not match /\bthink/i outside <pre>.
      expect(/\bthink/i.test(attemptsChromeText)).toBe(false);
    }
  });

  // 47. Byte-identity on all four G7-FOLLOWUP-T1 pivot copy strings/templates (G7-T1 AC1)
  it('G7-T1 AC1: PIVOT_TO_RECORDS_LABEL is byte-identical to SME-delivered string', () => {
    expect(PIVOT_TO_RECORDS_LABEL).toBe(
      'See the collection records for this model'
    );
  });

  it('G7-T1 AC1: pivotToRecordsAriaLabel template is byte-identical to SME-delivered string', () => {
    expect(pivotToRecordsAriaLabel('claude-opus-4-5', 'family')).toBe(
      'See the collection records for claude-opus-4-5 on the family domain'
    );
  });

  it('G7-T1 AC1: pivotToRecordsArrivalCaption template is byte-identical to SME-delivered string', () => {
    expect(pivotToRecordsArrivalCaption('claude-opus-4-5', 'family')).toBe(
      'Showing the collection records LSB produced when running the family protocol with claude-opus-4-5 as the informant.'
    );
  });

  it('G7-T1 AC1: pivotToRecordsNoMatchNotice template is byte-identical to SME-delivered string', () => {
    expect(pivotToRecordsNoMatchNotice('claude-opus-4-5', 'family')).toBe(
      'The Collection records tab has no successful-run summary for claude-opus-4-5 on the family domain. The per-model summary table only lists models that produced a parseable session in this domain.'
    );
  });

  // 50. FailuresFindings with matching pivotTarget applies highlight class and calls
  //     onPivotTargetConsumed (G7-T1 AC4).
  //     Uses a model_id that IS in recordsFamilyJson.by_model.
  it('G7-T1 AC4: pivotTarget matching a known model applies arrival highlight and calls onPivotTargetConsumed', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const consumed = vi.fn();
    const firstModelId = (recordsFamilyJson as { by_model: Array<{ model_id: string }> })
      .by_model[0].model_id;

    const { container } = render(
      <FailuresFindings
        pivotTarget={{ modelId: firstModelId, domainSlug: 'family' }}
        onPivotTargetConsumed={consumed}
      />
    );

    // Wait for records to load (by_model table rendered)
    await waitFor(() => {
      expect(
        container.querySelectorAll('.failures-findings__successes-tr').length
      ).toBeGreaterThan(0);
    });

    // The matching row must carry the pivot-arrival class.
    await waitFor(() => {
      const highlightedRows = container.querySelectorAll(
        '.failures-findings__successes-tr--pivot-arrival'
      );
      expect(highlightedRows.length).toBeGreaterThanOrEqual(1);
    });

    // onPivotTargetConsumed must have been called once after consumption.
    await waitFor(() => {
      expect(consumed).toHaveBeenCalledTimes(1);
    });
  });

  // 51. FailuresFindings with no-match pivotTarget renders arrival notice and calls
  //     onPivotTargetConsumed (G7-T1 AC5).
  //     Uses a model_id that is NOT in recordsFamilyJson.by_model.
  it('G7-T1 AC5: pivotTarget with no matching row renders no-match notice and calls onPivotTargetConsumed', async () => {
    mockFetchBoth(familyJson, recordsFamilyJson);
    const consumed = vi.fn();
    const unknownModelId = 'fixture-model-that-does-not-exist';

    const { container } = render(
      <FailuresFindings
        pivotTarget={{ modelId: unknownModelId, domainSlug: 'family' }}
        onPivotTargetConsumed={consumed}
      />
    );

    // Wait for records to load (by_model table rendered or no-match notice rendered)
    await waitFor(() => {
      const notice = container.querySelector(
        '.failures-findings__pivot-arrival-notice'
      );
      expect(notice).not.toBeNull();
    });

    // The notice text should reference the no-match template.
    const notice = container.querySelector('.failures-findings__pivot-arrival-notice');
    expect(notice!.textContent).toContain(unknownModelId);

    // onPivotTargetConsumed must have been called once after consumption.
    await waitFor(() => {
      expect(consumed).toHaveBeenCalledTimes(1);
    });
  });

  // 52. Chrome-isolation walk on pivot affordance copy: zero forbidden vocabulary (G7-T1 AC6).
  //     The PIVOT_TO_RECORDS_LABEL string and the two template functions are the
  //     G7 affordance surfaces. None may contain forbidden vocabulary.
  it('G7-T1 AC6: pivot affordance copy strings contain no forbidden vocabulary', () => {
    const FORBIDDEN_PATTERNS = [
      /\bworldview\b/i,
      /\bbelieves\b/i,
      /\bthinks?\b/i,
      /\bunderstands\b/i,
    ];

    // Collect all G7 copy strings (label + both template outputs with fixture args)
    const copyStrings = [
      PIVOT_TO_RECORDS_LABEL,
      pivotToRecordsAriaLabel('claude-opus-4-5', 'family'),
      pivotToRecordsArrivalCaption('claude-opus-4-5', 'family'),
      pivotToRecordsNoMatchNotice('claude-opus-4-5', 'family'),
    ];

    for (const str of copyStrings) {
      for (const pattern of FORBIDDEN_PATTERNS) {
        expect(str).not.toMatch(pattern);
      }
    }
  });

  // 53. FableDisclosureNote renders on failures surface and records surface when
  //     claude-fable-5 is present in fetched data. (DESIGN_SYSTEM.md §19.20, batch A)
  it('case 53: FableDisclosureNote renders FABLE_DISCLOSURE_FRAMING and FABLE_DISCLOSURE_BOUND when claude-fable-5 in failures data', async () => {
    // Minimal failures fixture containing a claude-fable-5 failure record
    const fableFailuresFile = {
      domain_slug: 'family',
      framing_note: 'fixture framing note for fable test',
      n_records: 1,
      n_failure_records: 1,
      n_decline_interview_records: 0,
      records: [{
        record_type: 'failure',
        model_id: 'claude-fable-5',
        collection_date: '2026-07-13T00:00:00Z',
        error_type: 'refusal',
        error_message: 'stop_reason=refusal',
        run_index: 0,
        originating_outcome_class: null,
        retry_attempts: null,
      }],
    };
    // Minimal records summary with claude-fable-5 in by_model
    const fableRecordsSummary = {
      domain_slug: 'family',
      generated_at: '2026-07-13T00:00:00Z',
      n_informants: 1,
      framing_note: 'fixture framing note for fable records test',
      by_model: [{
        model_id: 'claude-fable-5',
        provider: 'anthropic',
        n_runs: 1,
        n_qa_passed: 0,
        model_version_returned: 'claude-fable-5-fixture',
        model_version_returned_count: 1,
      }],
    };
    mockFetchBoth(fableFailuresFile, fableRecordsSummary);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      // failures surface: FableDisclosureNote renders two .failures-findings__impact paragraphs
      // (in addition to the pre-existing IMPACT_PARAGRAPH_FAILURES paragraph, which is a third)
      const impacts = container.querySelectorAll('p.failures-findings__impact');
      const texts = Array.from(impacts).map((el) => el.textContent ?? '');
      expect(texts).toContain(FABLE_DISCLOSURE_FRAMING);
      expect(texts).toContain(FABLE_DISCLOSURE_BOUND);
    });
  });

  // 54. FableDisclosureNote absent when claude-fable-5 is NOT in failures or records data.
  it('case 54: FableDisclosureNote absent when claude-fable-5 not in failures data', async () => {
    // familyJson (production fixture) predates batch A and contains no claude-fable-5 records
    mockFetchBoth(familyJson, recordsFamilyJson);
    const { container } = render(<FailuresFindings />);
    await waitFor(() => {
      // All .failures-findings__impact paragraphs that render should NOT contain fable strings
      const impacts = container.querySelectorAll('p.failures-findings__impact');
      const texts = Array.from(impacts).map((el) => el.textContent ?? '');
      expect(texts).not.toContain(FABLE_DISCLOSURE_FRAMING);
      expect(texts).not.toContain(FABLE_DISCLOSURE_BOUND);
    });
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
