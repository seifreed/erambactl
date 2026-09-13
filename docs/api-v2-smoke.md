# API v2 Smoke Evidence

Last verified local lab command:

```bash
PYTHON=/tmp/erambactl-venv/bin/python ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-api-v2-smoke
```

Verified result per instance:

| Instance | Total | JSON | HTTP 404 | HTTP 422 | HTTP 500 | Failures |
|---|---:|---:|---:|---:|---:|---:|
| local-a | 209 | 177 | 6 | 14 | 12 | 0 |
| local-b | 209 | 177 | 6 | 14 | 12 | 0 |

The smoke runner treats `route_404` and `http_405` as command metadata failures.
The verified run had none of either status. The remaining HTTP responses are
business/data validation responses from eramba after the command reached the
mounted route.
