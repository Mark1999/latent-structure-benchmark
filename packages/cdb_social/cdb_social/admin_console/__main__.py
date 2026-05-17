"""Entry point for ``python -m cdb_social.admin_console``.

Starts the Flask dev server bound to 127.0.0.1:8000 (loopback only).

Security posture: the bind address is hardcoded. This entry point does NOT
accept a ``--host`` argument. If you need to override, edit the source and
re-implement the security posture. The loopback bind is the security boundary;
no authentication is needed precisely because 127.0.0.1 is not reachable from
any other host.

Per Phase 7 kickoff §11.6 acceptance criteria and CDA SME T6b §5.x.
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from cdb_social.admin_console.app import create_app  # noqa: E402


def main() -> int:
    app = create_app()
    host = "127.0.0.1"
    port = 8000
    # Mandatory startup log per §11.6 acceptance criteria.
    # The literal string "127.0.0.1:8000 (loopback only; no internet exposure)"
    # is emitted verbatim so operators and tests can grep for it.
    _startup_msg = f"Listening on {host}:{port} (loopback only; no internet exposure)"
    logging.warning(_startup_msg)
    app.run(host=host, port=port, debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
