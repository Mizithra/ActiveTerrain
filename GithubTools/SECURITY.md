# Security Policy

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's private vulnerability reporting
(Security tab, then "Report a vulnerability") or email SECURITY_CONTACT@example.com (replace before publishing).

Please include the affected component (firmware, backend, UI, hardware), version or commit, reproduction steps, and impact.

## What to expect

- Acknowledgement within 7 days
- A status update within 30 days
- Credit in the release notes if you wish

## Supported versions

Only the latest release (firmware and hub software) receives security fixes. See the threat model in `docs/security/`.

## Scope

In scope: firmware, backend, UI, provisioning and update mechanisms, broker configuration shipped with the project.
Out of scope: physical attacks requiring disassembly of a production unit (tracked separately), third-party services.
