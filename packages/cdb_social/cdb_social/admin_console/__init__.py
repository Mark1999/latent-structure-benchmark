"""Admin console package for the LSB social publishing pipeline.

Local-only Flask web UI that lets Mark act on detected triggers and the queue.
Drafting happens here on Mark's explicit per-trigger request; approving and
publishing are two distinct button-clicks.

Bind posture: loopback-only (127.0.0.1:8000). No authentication needed;
no TLS needed; no internet exposure. The loopback bind is the security boundary.

Per Phase 7 kickoff §11.6 and CDA SME T6b §5.1-§5.10 binding notes.
"""

from cdb_social.admin_console.app import create_app

__all__ = ["create_app"]
