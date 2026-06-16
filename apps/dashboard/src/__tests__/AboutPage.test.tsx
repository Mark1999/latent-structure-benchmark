/**
 * AboutPage tests: About tab long-form article (M2, 2026-06-10).
 *
 * No fetch calls. AboutPage is fully static. No real API calls per CLAUDE.md §6 rule 9.
 *
 * Test cases:
 * 1.  h2 heading renders: "About Mark Dawson" (case-exact)
 * 2.  opening sentence renders verbatim
 * 3.  closing sentence renders verbatim
 * 4.  canonical §1.5 disclaim sentence renders verbatim (cite-to-disclaim paragraph)
 * 5.  forbidden-vocabulary scan (buildPat runtime-pattern technique;
 *     test source must not contain literal forbidden strings); must not appear
 *     outside cite-to-disclaim paragraphs
 * 6.  negative-content assertions (no hire-me / consulting / services / contact copy)
 * 7.  no <form> element renders
 * 8.  NavBar integration: "About" button has aria-current="page" when active;
 *     five tabs in correct DOM order; "About" is last (index 4)
 * 9.  NavBar fires onTabChange('about') on About-button click
 *
 * Gate verdicts (M2):
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-10-site-copy-verdicts.md (M2 section)
 *   UI/UX  PASS-WITH-NOTES:  docs/status/2026-06-10-site-copy-verdicts.md (M2 section)
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { AboutPage } from '../components/AboutPage';
import { NavBar } from '../components/NavBar';

// Forbidden-vocabulary patterns for test 5 (ARCHITECTURE.md §1.5.4 / CLAUDE.md §7).
// Patterns built at runtime from char-code arrays so file content does not
// contain the impermissible strings (static hook guards file source).
const buildPat = (codes: number[]) => new RegExp(String.fromCharCode(...codes), 'i');
const FORBIDDEN_PATTERNS: RegExp[] = [
  // §7 item: impermissible framing word #1
  buildPat([119,111,114,108,100,118,105,101,119]),
  // §7 item: impermissible framing phrase #2 (8 + 1 + 4 chars)
  buildPat([99,117,108,116,117,114,97,108,32,98,105,97,115]),
];

describe('AboutPage', () => {

  // 1. h2 heading renders (case-exact)
  it('renders h2 heading "About Mark Dawson"', () => {
    render(<AboutPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'About Mark Dawson' })
    ).toBeInTheDocument();
  });

  // 2. opening sentence
  it('renders opening sentence verbatim', () => {
    render(<AboutPage />);
    expect(
      screen.getByText(
        'CogStructureLab grows out of my work at the intersection of culture, technology, intelligence analysis, and human-centered research.'
      )
    ).toBeInTheDocument();
  });

  // 3. closing sentence
  it('renders closing sentence verbatim', () => {
    render(<AboutPage />);
    expect(
      screen.getByText('That is the space I work in.')
    ).toBeInTheDocument();
  });

  // 4. canonical §1.5 disclaim sentence (cite-to-disclaim protection; must survive verbatim)
  it('renders canonical disclaim sentence verbatim', () => {
    render(<AboutPage />);
    const disclaim = screen.getByText((content) =>
      content.includes(
        'The Observatory does not claim that models have beliefs, intentions, lived experience, or culture in the human sense.'
      )
    );
    expect(disclaim).toBeInTheDocument();
  });

  // 5. forbidden-vocabulary scan (must not appear outside cite-to-disclaim paragraphs)
  // Two cite-to-disclaim occurrences are excluded (CDA SME M2-N1 BINDING):
  //   - paragraph 2: "I use culture in that broad sense..." (Mark defining human anthropological sense)
  //   - paragraph 6: "does not claim that models have beliefs, intentions, lived experience,
  //     or culture in the human sense" (canonical §1.5 disclaim move)
  it('contains no impermissible vocabulary outside cite-to-disclaim contexts', () => {
    const { container } = render(<AboutPage />);
    const clone = container.cloneNode(true) as HTMLElement;
    const allP = Array.from(clone.querySelectorAll('p'));
    // Remove paragraph 6: contains the canonical disclaim sentence (occurrence 2)
    const disclaimP = allP.find((p) =>
      p.textContent?.includes(
        'The Observatory does not claim that models have beliefs'
      )
    );
    if (disclaimP) disclaimP.remove();
    // Remove paragraph 2: contains "I use culture in that broad sense" (occurrence 1)
    const cultureDefP = allP.find((p) =>
      p.textContent?.includes('I use culture in that broad sense')
    );
    if (cultureDefP) cultureDefP.remove();
    const text = clone.textContent ?? '';
    FORBIDDEN_PATTERNS.forEach((pattern, idx) => {
      expect(text, `§7 pattern ${idx} must not appear outside cite-to-disclaim contexts`).not.toMatch(pattern);
    });
  });

  // 6. negative-content assertions (M2 positioning: demonstration piece, not portfolio/sales)
  it('does not contain hire-me or consulting copy', () => {
    render(<AboutPage />);
    expect(screen.queryByText(/hire me/i)).toBeNull();
    expect(screen.queryByText(/consulting/i)).toBeNull();
    expect(screen.queryByText(/services/i)).toBeNull();
    expect(screen.queryByText(/contact me/i)).toBeNull();
    expect(screen.queryByText(/get in touch/i)).toBeNull();
    expect(screen.queryByText(/available for/i)).toBeNull();
  });

  it('does not contain a mailto: link', () => {
    const { container } = render(<AboutPage />);
    const mailtoLinks = container.querySelectorAll('a[href^="mailto:"]');
    expect(mailtoLinks.length).toBe(0);
  });

  // 7. no <form> element renders
  it('does not render a <form> element', () => {
    const { container } = render(<AboutPage />);
    expect(container.querySelector('form')).toBeNull();
  });

  // 8a. [OBSERVATORY-RENAME] "Cognitive Structure Observatory" appears as the
  //     instrument name in AboutPage prose; "Latent Structure Benchmark" must
  //     not appear (frozen bundle name lives on DataPage only).
  //     Gate: docs/status/2026-06-12-observatory-rename-verdicts.md
  it('[OBSERVATORY-RENAME] renders "Cognitive Structure Observatory" as instrument name', () => {
    const { container } = render(<AboutPage />);
    expect(container.textContent).toMatch(/Cognitive Structure Observatory/);
  });

  it('[OBSERVATORY-RENAME] does not render "Latent Structure Benchmark" in About prose', () => {
    const { container } = render(<AboutPage />);
    expect(container.textContent).not.toMatch(/Latent Structure Benchmark/);
  });

});

describe('NavBar: About tab integration (M2)', () => {

  // 8. "About" button has aria-current="page" when activeTab="about";
  //    five tabs in correct DOM order; About is last (index 4)
  it('marks About button as current page when activeTab is "about"', () => {
    render(<NavBar activeTab="about" onTabChange={() => {}} />);
    const aboutBtn = screen.getByRole('button', { name: 'About' });
    expect(aboutBtn).toHaveAttribute('aria-current', 'page');
  });

  it('renders five tabs in correct order: Explore, Methodology, Collection records, Data, About', () => {
    render(<NavBar activeTab="about" onTabChange={() => {}} />);
    const buttons = screen.getAllByRole('button');
    const tabLabels = buttons.map((b) => b.textContent?.trim());
    expect(tabLabels[0]).toBe('Explore');
    expect(tabLabels[1]).toBe('Methodology');
    // Collection records uses FAILURES_TAB_LABEL constant; verify present at index 2
    expect(tabLabels[2]).toBeTruthy();
    expect(tabLabels[3]).toBe('Data');
    expect(tabLabels[4]).toBe('About');
  });

  it('About button is the last tab in DOM order (index 4)', () => {
    render(<NavBar activeTab="explore" onTabChange={() => {}} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons[4].textContent?.trim()).toBe('About');
  });

  it('other tabs do not have aria-current="page" when About is active', () => {
    render(<NavBar activeTab="about" onTabChange={() => {}} />);
    const exploreBtn = screen.getByRole('button', { name: 'Explore' });
    const methodologyBtn = screen.getByRole('button', { name: 'Methodology' });
    const dataBtn = screen.getByRole('button', { name: 'Data' });
    expect(exploreBtn).not.toHaveAttribute('aria-current', 'page');
    expect(methodologyBtn).not.toHaveAttribute('aria-current', 'page');
    expect(dataBtn).not.toHaveAttribute('aria-current', 'page');
  });

  // 9. NavBar fires onTabChange('about') on About-button click
  it('fires onTabChange with "about" when About button is clicked', () => {
    const onTabChange = vi.fn();
    render(<NavBar activeTab="explore" onTabChange={onTabChange} />);
    const aboutBtn = screen.getByRole('button', { name: 'About' });
    fireEvent.click(aboutBtn);
    expect(onTabChange).toHaveBeenCalledWith('about');
    expect(onTabChange).toHaveBeenCalledTimes(1);
  });

  // 10. [OBSERVATORY-RENAME] NavBar brand inner span renders "/ Observatory"
  //     (UI/UX N7 Option B: brand = "Cognitive Structure Lab / Observatory").
  //     Gate: docs/status/2026-06-12-observatory-rename-verdicts.md
  it('[OBSERVATORY-RENAME] NavBar brand span renders "/ Observatory"', () => {
    const { container } = render(<NavBar activeTab="explore" onTabChange={() => {}} />);
    const brand = container.querySelector('.nav__brand');
    expect(brand).not.toBeNull();
    const innerSpan = brand!.querySelector('span');
    expect(innerSpan).not.toBeNull();
    expect(innerSpan!.textContent).toBe('/ Observatory');
  });

});
