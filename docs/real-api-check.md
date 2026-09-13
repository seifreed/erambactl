# Real API Check

Latest recorded run: 2026-09-13.

Command:

```bash
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-real-api-check
```

Current result:

- Bootstrap enabled API access for `admin` on both Docker lab instances.
- Full real seed data ran against `local-a` and `local-b`.
- Docker lab image: Eramba Community `3.31.0`.
- Real CLI API v2 strict non-destructive check ran `408` command executions
  across both instances: `408` OK.
- Known upstream/runtime actions ran in non-strict mode across both instances:
  `4` HTTP 500 responses from Eramba.
- Real CLI DELETE check ran `2` command executions across both instances: `2`
  OK.
- `post-settings-reset-application-id` ran across both instances: `2` OK.
- `post-settings-reset-database` ran across both instances: `2` OK.
- After `post-settings-reset-database`, both lab URLs still returned HTTP 302
  and Docker still answered `docker info`.

Remaining upstream/runtime failures:

- `get-settings-activate-license`: the Docker lab does not have a valid Eramba
  Enterprise license to activate. Eramba Community reports itself as already
  activated, so `LicenseService::activateLicense()` raises
  `Unable to activate a SaaS deployment.`
- `get-filters-id-timestamp`: Eramba raises a return type error, returning a
  `Carbon` value where `FilterRepository::getFilterTimestamp()` declares
  `string`.

Notes:

- `scripts/eramba-real-api-check` uses `eramba-real-cli-check`, not the smoke
  runner, for API command verification.
- `scripts/eramba-real-api-check` continues through all API v2 phases and exits
  non-zero at the end if any project-check phase reported failures. Known
  upstream/runtime 500s are still exercised, but outside the strict pass.
- The check uses seeded IDs and endpoint-specific payloads, not dry-run dummy
  values.
- Destructive reset endpoints are executed after the broad API v2 pass.
