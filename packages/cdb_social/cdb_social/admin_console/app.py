"""Flask app factory for the LSB admin console.

Per Phase 7 kickoff §11.6:
- Binds to 127.0.0.1 only (loopback; no internet exposure).
- CSRF protection via Flask's built-in session signing (secrets-based).
- No authentication needed; loopback bind is the security boundary.
- No TLS needed.
"""

from __future__ import annotations

import secrets
from pathlib import Path

from flask import Flask


def create_app() -> Flask:
    """Construct and configure the admin console Flask app."""
    template_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )

    # CSRF protection via Flask's built-in session signing.
    # Per-process secret: regenerated on each server restart. This is
    # intentional — sessions are ephemeral (the admin console is a
    # loopback-bound dev-server, not a persistent web service).
    app.config["SECRET_KEY"] = secrets.token_hex(32)

    from cdb_social.admin_console.routes import bp  # noqa: PLC0415

    app.register_blueprint(bp)

    return app
