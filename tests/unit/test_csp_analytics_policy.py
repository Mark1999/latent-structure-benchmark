"""Doc-contract tests for the §2.7 Web Analytics (Insights) policy.

The §2.7 section added to HOSTING_AND_DEV_OPS.md makes factual claims about
the content of apps/dashboard/public/_headers. These tests verify those
claims so that if _headers is modified in a way that would invalidate the
§2.7 rationale, this test suite catches it before the doc drifts silently.

No real API calls. No model calls. Pure filesystem reads.
"""

from pathlib import Path

# Repo root: two levels up from tests/unit/
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

HEADERS_FILE = REPO_ROOT / "apps" / "dashboard" / "public" / "_headers"
HOSTING_DOC = REPO_ROOT / "HOSTING_AND_DEV_OPS.md"


class TestHeadersFileExistsAndContainsExpectedDirectives:
    """The _headers file must exist and must contain the CSP directives
    that §2.7 cites as the reason analytics auto-injection must stay OFF."""

    def test_headers_file_exists(self) -> None:
        assert HEADERS_FILE.exists(), (
            f"_headers file not found at {HEADERS_FILE}. "
            "HOSTING_AND_DEV_OPS.md §2.7 cites this file's CSP as the basis "
            "for disabling Cloudflare Web Analytics auto-injection."
        )

    def test_connect_src_self_is_present(self) -> None:
        """connect-src 'self' must appear in the CSP.

        §2.7 states: "connect-src 'self' is the architectural commitment from
        ARCHITECTURE.md §4.5 ... no telemetry." If this directive is widened,
        §2.7's rationale no longer holds and the section must be revised.
        """
        content = HEADERS_FILE.read_text()
        assert "connect-src 'self'" in content, (
            "_headers does not contain \"connect-src 'self'\". "
            "HOSTING_AND_DEV_OPS.md §2.7 relies on this directive to justify "
            "keeping Cloudflare Web Analytics auto-injection OFF. "
            "If the directive changed, update §2.7 accordingly."
        )

    def test_script_src_self_is_present(self) -> None:
        """script-src 'self' must appear in the CSP.

        §2.7 states: "script-src 'self' restricts scripts to same-origin only."
        The beacon from static.cloudflareinsights.com would be blocked by this.
        """
        content = HEADERS_FILE.read_text()
        assert "script-src 'self'" in content, (
            "_headers does not contain \"script-src 'self'\". "
            "HOSTING_AND_DEV_OPS.md §2.7 relies on this directive to explain "
            "why the analytics beacon script is blocked. "
            "If the directive changed, update §2.7 accordingly."
        )

    def test_cloudflareinsights_not_permitted_in_csp(self) -> None:
        """cloudflareinsights.com must not appear in the _headers CSP.

        §2.7 documents that auto-injection is OFF precisely because the beacon
        would be blocked by the CSP. If cloudflareinsights.com were ever added
        to connect-src or script-src, analytics would be implicitly re-enabled
        and §2.7 would need a full three-co-update revision.
        """
        content = HEADERS_FILE.read_text()
        assert "cloudflareinsights" not in content, (
            "_headers contains 'cloudflareinsights', which means the analytics "
            "beacon domain has been permitted in the CSP. "
            "HOSTING_AND_DEV_OPS.md §2.7 policy requires three co-updates "
            "(Architect sign-off + _headers change + SECURITY_AND_HARDENING.md §3.1 "
            "update) to re-enable analytics. Verify all three co-updates are present."
        )


class TestHostingDocContainsAnalyticsSection:
    """The §2.7 section must be present in HOSTING_AND_DEV_OPS.md.

    If the section is removed or renamed without the three co-updates required
    by §2.7 itself, this test will fail and flag the omission.
    """

    def test_hosting_doc_exists(self) -> None:
        assert HOSTING_DOC.exists(), (
            f"HOSTING_AND_DEV_OPS.md not found at {HOSTING_DOC}."
        )

    def test_section_2_7_heading_present(self) -> None:
        content = HOSTING_DOC.read_text()
        assert "### 2.7" in content, (
            "HOSTING_AND_DEV_OPS.md does not contain the '### 2.7' heading. "
            "The Web Analytics policy section has been removed or renumbered. "
            "Verify the policy is documented somewhere in the file."
        )

    def test_section_2_7_mentions_auto_injection(self) -> None:
        content = HOSTING_DOC.read_text()
        assert "auto-injection" in content, (
            "HOSTING_AND_DEV_OPS.md no longer mentions 'auto-injection'. "
            "The §2.7 policy text has been removed or substantially rewritten. "
            "Verify the Cloudflare Web Analytics disable policy is still documented."
        )

    def test_section_2_7_mentions_csp_rationale(self) -> None:
        """§2.7 must reference the CSP directives as the rationale."""
        content = HOSTING_DOC.read_text()
        # Both directives should appear in the hosting doc (in §2.7)
        assert "connect-src" in content, (
            "HOSTING_AND_DEV_OPS.md §2.7 no longer mentions 'connect-src'. "
            "The CSP rationale for disabling analytics has been removed."
        )
        assert "script-src" in content, (
            "HOSTING_AND_DEV_OPS.md §2.7 no longer mentions 'script-src'. "
            "The CSP rationale for disabling analytics has been removed."
        )

    def test_changelog_entry_v015_present(self) -> None:
        """The v0.1.5 changelog entry must be present.

        The §2.7 commit also added a changelog entry. If someone removes the
        changelog or the version entry without a matching version bump, this
        test flags the inconsistency.
        """
        content = HOSTING_DOC.read_text()
        assert "v0.1.5" in content, (
            "HOSTING_AND_DEV_OPS.md does not contain the 'v0.1.5' changelog entry. "
            "If the document was restructured, verify the analytics policy history "
            "is still captured in the changelog."
        )
