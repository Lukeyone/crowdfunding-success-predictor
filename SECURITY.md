# Security Policy

## Credentials

This repository does not contain or require shared Google Cloud credentials.

Do not commit API keys, service-account JSON files, private keys, passwords,
access tokens or local `.env` files. Anyone adding an external integration
must create and configure their own account and credentials.

Before committing, run:

```bash
git status
git diff --cached
```

Confirm that no credential or private configuration file is staged.

## Reporting a Security Issue

Report suspected credential exposure privately to `lachornot@gmail.com`.
Do not publish an active credential in a GitHub issue.
