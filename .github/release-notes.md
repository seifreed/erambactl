# erambactl 0.1.0

This is the first public release of erambactl, a small Python tool for working
with eramba from the command line or from Python code.

## Highlights

- Command catalog for eramba API routes, including 209 API v2 commands.
- Multi-instance support for running the same command across several eramba
  deployments.
- Authentication with bearer tokens, session login, cookies, and HTTP Basic.
- Request support for path parameters, query strings, JSON bodies, form fields,
  file uploads, custom headers, and eramba dry-run requests.
- Local two-instance Docker lab based on eramba's official Docker deployment.
- Seed, smoke, and real CLI checks for validating API behavior against running
  eramba instances.
- No runtime Python dependencies.
- CI coverage for Ubuntu, Windows, and macOS on Python 3.14.

The package is published to PyPI and the GitHub release includes the source
distribution and wheel built by the release workflow.
