<p align="center">
  <img src="https://img.shields.io/badge/erambactl-eramba%20API%20CLI-blue?style=for-the-badge" alt="erambactl">
</p>

<h1 align="center">erambactl</h1>

<p align="center">
  <strong>Command-line access to eramba's API, with multi-instance support</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/erambactl/"><img src="https://img.shields.io/pypi/v/erambactl?style=flat-square&logo=pypi&logoColor=white" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/erambactl/"><img src="https://img.shields.io/pypi/pyversions/erambactl?style=flat-square&logo=python&logoColor=white" alt="Python Versions"></a>
  <a href="https://github.com/seifreed/erambactl/blob/main/pyproject.toml"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://github.com/seifreed/erambactl/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/seifreed/erambactl/ci.yml?style=flat-square&logo=github&label=CI" alt="CI Status"></a>
  <a href="https://github.com/seifreed/erambactl"><img src="https://img.shields.io/badge/runtime%20deps-none-brightgreen?style=flat-square" alt="Runtime Dependencies"></a>
  <a href="https://github.com/seifreed/erambactl"><img src="https://img.shields.io/badge/coverage-100%25-brightgreen?style=flat-square" alt="Coverage"></a>
</p>

<p align="center">
  <a href="https://github.com/seifreed/erambactl/stargazers"><img src="https://img.shields.io/github/stars/seifreed/erambactl?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/seifreed/erambactl/issues"><img src="https://img.shields.io/github/issues/seifreed/erambactl?style=flat-square" alt="GitHub Issues"></a>
  <a href="https://buymeacoffee.com/seifreed"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-support-yellow?style=flat-square&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee"></a>
</p>

---

## Overview

**erambactl** is a Python 3.14 command-line tool and library for automating
eramba through its HTTP API. It ships with a checked-in catalog of eramba API
routes, including API v2, and does not depend on OpenAPI at runtime.

Use it against one eramba instance, or run the same command across several
configured instances for lab work, regression checks, and repeatable admin
tasks.

### Key Features

| Feature | Description |
|---------|-------------|
| **Route Commands** | One CLI command per checked-in eramba route catalog entry |
| **API v2 Catalog** | 209 `api-v2` commands with documented methods, paths, and flags |
| **Full API Catalog** | 1592 total commands across legacy `api` and `api-v2` groups |
| **No Runtime OpenAPI** | Commands use the local catalog, not a live OpenAPI schema |
| **Multi-instance** | Run login, API, seed, smoke, and real CLI checks against one or all instances |
| **Auth Modes** | Bearer token, web session login, Cookie support, and HTTP Basic header mode |
| **Payload Support** | Query params, JSON bodies, raw files, forms, uploads, headers, and dry-run |
| **Local Lab** | Two-instance Docker lab based on eramba's official Docker deployment |
| **CLI + Library** | Use it from a shell or import it as a Python package |

### What It Covers

```text
Commands        api, api-v2, login, commands
Inputs          path params, query params, JSON, files, forms, uploads
Auth            bearer, session login, basic, cookie
Instances       single instance, named instance, all instances
Checks          smoke checks, real CLI checks, route catalog checks
Packaging       wheel build and installed-console-script verification
```

---

## Installation

### From PyPI

```bash
pip install erambactl
```

### From Source

```bash
git clone https://github.com/seifreed/erambactl.git
cd erambactl
python3.14 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install -e ".[dev]"
```

### Optional Extras

The regular package has no runtime Python dependencies. Development tooling is
defined in the same `pyproject.toml` dependency file:

```bash
python -m pip install -e ".[dev]"
```

### Build a Wheel

```bash
python -m pip wheel . --wheel-dir dist
PYTHON=python3.14 scripts/eramba-package-check
```

```bat
scripts\eramba-package-check.cmd
```

---

## Quick Start

```bash
# List API v2 commands
erambactl commands --group api-v2

# Run an API v2 command against one instance
erambactl --config examples/instances.json --instance local-a api-v2 get-assets-index

# Run a command across all configured instances
erambactl --config examples/instances.json --all-instances api get-assets-index

# Send query params and eramba's dry-run header
erambactl --config examples/instances.json --instance local-a api get-assets-bulk-update-get --query "ids[]=1" --dry-run
```

---

## Usage

### Command Line Interface

```bash
# Bearer token auth
erambactl --base-url https://localhost:8443 --token "$ERAMBA_TOKEN" api-v2 get-assets-index

# Session login
erambactl --base-url https://localhost:8443 --username "$ERAMBA_USER" --password "$ERAMBA_PASS" login

# Cookie auth
erambactl --base-url https://localhost:8443 --cookie "$ERAMBA_COOKIE" --timeout 5 api-v2 get-settings-version

# JSON body from a file
erambactl --config examples/instances.json --instance local-a api-v2 put-assets-edit-id --id 1 --data-file asset.json

# Multipart form upload
erambactl --config examples/instances.json --instance local-a api post-attachments-store-form-create Assets file --form name=Evidence --file attachment=evidence.pdf
```

### Commands

| Command | Description |
|---------|-------------|
| `erambactl login` | Authenticate and print the session result |
| `erambactl api <command>` | Run an eramba API command |
| `erambactl api-v2 <command>` | Run an eramba API v2 command |
| `erambactl commands` | Print or filter the static command catalog |
| `erambactl-route-data` | Parse Laravel routes and verify the route catalog |
| `erambactl-seed` | Execute JSON seed fixtures against eramba |
| `erambactl-smoke` | Probe command catalogs against real eramba instances |
| `erambactl-real-cli-check` | Run the real CLI parser/request path command by command |

### Request Flags

| Option | Description |
|--------|-------------|
| `--query name=value` | Add query parameters |
| `--data <json>` | Send a JSON request body |
| `--data-file <file>` | Read a JSON or raw request body from disk |
| `--form name=value` | Add multipart form fields |
| `--file field=path` | Upload files in multipart requests |
| `--header name=value` | Add custom HTTP headers |
| `--dry-run` | Send eramba's Swagger dry-run header |

Path parameters can be passed positionally or with endpoint-specific flags such
as `--id`. API v2 commands with a request body accept the generic payload flags
above; commands with known body fields can also build JSON from field flags.

### API v2 Coverage

```text
API v2 commands                         209
Methods                                 DELETE 1, GET 177, POST 11, PUT 20
Commands with path parameters           39
Commands accepting a request body       32
Body command specs covered              32
Body commands with payload field flags  28
Body action commands without fields     4
```

See [docs/api-v2-commands.md](docs/api-v2-commands.md) for the generated API v2
command reference.

---

## Local eramba Lab

The repository includes a two-instance lab for testing multi-instance runs:

```text
local-a  https://localhost:8443
local-b  https://localhost:9443
```

```bash
scripts/eramba-lab up
scripts/eramba-lab bootstrap
scripts/eramba-lab ps
scripts/eramba-lab down
```

```bat
scripts\eramba-lab.cmd up
scripts\eramba-lab.cmd bootstrap
scripts\eramba-lab.cmd ps
scripts\eramba-lab.cmd down
```

The lab uses `https://github.com/eramba/docker` as the upstream source. The
project overrides bind public ports to `127.0.0.1` and pin eramba lab images by
digest.

---

## Seed and Smoke Checks

### Seed Data

```bash
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-seed-data --all-instances
erambactl-seed --config examples/instances.json --fixture examples/seed-data.json --all-instances
```

```bat
scripts\eramba-seed-data.cmd --all-instances
```

Seed fixtures are JSON command lists executed through the real erambactl client
against one or every configured eramba instance. No mock clients, no OpenAPI.

### Smoke Checks

```bash
ERAMBA_A_PASSWORD=admin scripts/eramba-api-smoke --instance local-a --limit 25
ERAMBA_B_PASSWORD=admin scripts/eramba-api-smoke --instance local-b --limit 25
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin erambactl-smoke --all-instances --all --group api-v2 --summary-only
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-api-v2-smoke
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-real-api-check
```

```bat
scripts\eramba-api-smoke.cmd --instance local-a --limit 25
scripts\eramba-api-v2-smoke.cmd
scripts\eramba-real-api-check.cmd
```

`erambactl-smoke` reports JSON, binary responses, HTTP errors, route 404s, and
transport failures. Use `--offset`, `--limit`, `--method`, `--resource`,
`--group`, `--path-value`, `--skip-method`, and `--summary-only` for batching.

### Real CLI Checks

```bash
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-real-api-check
ERAMBA_A_PASSWORD=admin ERAMBA_B_PASSWORD=admin scripts/eramba-real-cli-check --all-instances --group api-v2 --dry-run --path-value id=0
```

```bat
scripts\eramba-real-api-check.cmd
scripts\eramba-real-cli-check.cmd --all-instances --group api-v2 --dry-run --path-value id=0
```

`erambactl-real-cli-check` runs the real CLI parser and request path against
configured eramba instances. See [docs/api-v2-smoke.md](docs/api-v2-smoke.md)
and [docs/real-api-check.md](docs/real-api-check.md) for lab evidence.

---

## Route Catalog Maintenance

```bash
docker cp erambactl-a-eramba:/var/www/eramba/laravel/routes/api.php /tmp/eramba-api.php
erambactl-route-data /tmp/eramba-api.php
erambactl-route-data /tmp/eramba-api.php --print > erambactl/route_data.py
```

`erambactl-route-data` parses eramba's Laravel routes directly and verifies the
static catalog command by command. It does not use OpenAPI.

---

## Python Library

### Basic Usage

```python
from erambactl import ErambaClient, ErambaInstance, get_command

client = ErambaClient(
    ErambaInstance(
        name="local-a",
        base_url="https://localhost:8443",
        username="admin",
        password="admin",
        verify_tls=False,
        timeout=5,
    )
)

assets = client.request("GET", "/laravel/api/assets/index")
assets_v2 = client.run(get_command("get-assets-index", group="api-v2"))
```

### Multi-instance Usage

```python
from erambactl import ErambaFleet, ErambaInstance, get_command

fleet = ErambaFleet(
    (
        ErambaInstance(
            name="local-a",
            base_url="https://localhost:8443",
            username="admin",
            password="admin",
            verify_tls=False,
            timeout=5,
        ),
        ErambaInstance(
            name="local-b",
            base_url="https://localhost:9443",
            username="admin",
            password="admin",
            verify_tls=False,
            timeout=5,
        ),
    )
)

command = get_command("get-assets-index", group="api-v2")
assets = fleet.run("local-a", command)
all_assets = fleet.run_all(command)
```

### File Uploads

```python
from pathlib import Path

from erambactl import ErambaClient, ErambaInstance, UploadFile

client = ErambaClient(
    ErambaInstance(
        name="local-a",
        base_url="https://localhost:8443",
        token="token",
        verify_tls=False,
    )
)

client.request(
    "POST",
    "/laravel/api/attachments/form-add/Assets/file",
    form={"name": "Evidence"},
    files=(UploadFile("attachment", Path("evidence.pdf")),),
)
```

---

## CI

The project CI runs on Ubuntu, Windows, and macOS with Python 3.14:

```bash
black --check .
ruff check .
mypy .
bandit -r .
pip-audit .
pytest -q
scripts/eramba-package-check
```

The test suite is configured to fail below 100% coverage.

---

## Releases

Tagged releases build a source distribution and wheel, create a GitHub Release,
and publish to PyPI with Trusted Publishing/OIDC:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Configure the PyPI trusted publisher with:

```text
Project name: erambactl
Owner: seifreed
Repository: erambactl
Workflow: release.yml
Environment: pypi
```

The release workflow does not use a PyPI API token.

---

## Requirements

- Python 3.14 exactly
- Windows, Linux, and macOS support
- No runtime Python dependencies
- Docker, when using the local eramba lab
- See [pyproject.toml](pyproject.toml) for development tooling

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Support the Project

If this project is useful in your workflows, you can support development:

<a href="https://buymeacoffee.com/seifreed" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>

---

## License

This project is licensed under the MIT license. See [pyproject.toml](pyproject.toml).

**Attribution**

- Author: **Seif Reed** | [@seifreed](https://github.com/seifreed)
- Repository: [github.com/seifreed/erambactl](https://github.com/seifreed/erambactl)

---

<p align="center">
  <sub>Made for eramba API checks, lab setup, and day-to-day automation</sub>
</p>
