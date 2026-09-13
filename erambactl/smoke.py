from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from erambactl._shared import add_check_arguments, command_window, error_summary
from erambactl._shared import pair_dict as _pairs
from erambactl.client import ErambaClient, ErambaError
from erambactl.commands import API_COMMANDS, ApiCommand, format_command_path
from erambactl.config import load_fleet, load_instance
from erambactl.types import ApiResult, JsonValue, Query


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    report = _report(args, parser)
    if args.summary_only:
        report = _summary(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if _has_failures(report) else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    add_check_arguments(parser)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    return parser


def _report(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> dict[str, object]:
    commands = _commands(
        args.all,
        args.limit,
        args.offset,
        args.method,
        args.resource,
        args.group,
        args.skip_method,
    )
    path_values = _pairs(args.path_value, "path value")

    if args.all_instances:
        return _run_fleet(args.config, commands, args.dry_run, path_values)
    if args.instance is not None:
        return run_smoke(
            ErambaClient(load_instance(args.config, args.instance)),
            args.instance,
            commands,
            args.dry_run,
            path_values,
        )
    parser.error("Use --instance or --all-instances")


def _run_fleet(
    path: Path,
    commands: tuple[ApiCommand, ...],
    dry_run: bool = False,
    path_values: dict[str, str] | None = None,
) -> dict[str, object]:
    fleet = load_fleet(path)
    reports = tuple(
        run_smoke(fleet.client(name), name, commands, dry_run, path_values)
        for name in fleet.names()
    )
    return {
        "instances": reports,
        "total_instances": len(reports),
        "failures": [
            failure
            for report in reports
            for failure in cast(list[dict[str, str]], report["failures"])
        ],
    }


def _has_failures(report: dict[str, object]) -> bool:
    if "instances" in report:
        instances = cast(tuple[dict[str, object], ...], report["instances"])
        return bool(report["failures"]) or any(_has_failures(instance) for instance in instances)
    results = cast(dict[str, int], report["results"])
    return bool(report["failures"]) or any(
        results.get(status, 0) > 0 for status in ("route_404", "http_405")
    )


def _summary(report: dict[str, object]) -> dict[str, object]:
    if "instances" in report:
        instances = cast(tuple[dict[str, object], ...], report["instances"])
        return {
            "instances": tuple(_summary(instance) for instance in instances),
            "total_instances": report["total_instances"],
            "failures": len(cast(list[dict[str, str]], report["failures"])),
        }
    return {
        "instance": report["instance"],
        "total": report["total"],
        "results": report["results"],
        "http_errors": len(cast(list[dict[str, str]], report["http_errors"])),
        "failures": len(cast(list[dict[str, str]], report["failures"])),
    }


def run_smoke(
    client: ErambaClient,
    instance: str,
    commands: tuple[ApiCommand, ...],
    dry_run: bool = False,
    path_values: dict[str, str] | None = None,
) -> dict[str, object]:
    results: dict[str, int] = {}
    probes: list[dict[str, str]] = []
    http_errors: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    for command in commands:
        path, status, http_error, failure = _run_probe(client, command, dry_run, path_values)
        if http_error is not None:
            http_errors.append(http_error)
        if failure is not None:
            failures.append(failure)
        probes.append(_probe(command, path, status))
        results[status] = results.get(status, 0) + 1

    return {
        "instance": instance,
        "total": len(commands),
        "results": results,
        "probes": probes,
        "http_errors": http_errors,
        "failures": failures,
    }


def _run_probe(
    client: ErambaClient,
    command: ApiCommand,
    dry_run: bool,
    path_values: dict[str, str] | None,
) -> tuple[str, str, dict[str, str] | None, dict[str, str] | None]:
    path = _path(command, path_values)
    try:
        result = client.request(
            command.method,
            path,
            query=_query(command),
            body=_body(command),
            headers=_headers(dry_run),
        )
    except ErambaError as error:
        return path, _error_status(error), _failure(command, error), None
    except (TimeoutError, OSError, ValueError) as error:
        return path, type(error).__name__, None, _failure(command, error)
    return path, _result_status(result), None, None


def _commands(
    include_all: bool,
    limit: int | None,
    offset: int = 0,
    method: str | None = None,
    resource: str | None = None,
    group: str | None = None,
    skip_methods: list[str] | None = None,
) -> tuple[ApiCommand, ...]:
    commands = API_COMMANDS if include_all else _safe_get_commands()
    skipped = {item.upper() for item in skip_methods or ()}
    filtered = tuple(
        command
        for command in commands
        if (group is None or command.group == group)
        and (method is None or command.method == method.upper())
        and command.method not in skipped
        and (resource is None or command.resource == resource)
    )
    return command_window(filtered, limit, offset)


def _safe_get_commands() -> tuple[ApiCommand, ...]:
    return tuple(
        command for command in API_COMMANDS if command.method == "GET" and not command.path_params
    )


def _failure(command: ApiCommand, error: BaseException) -> dict[str, str]:
    return {
        "action": command.action,
        "resource": command.resource,
        "error": error_summary(error),
    }


def _error_status(error: ErambaError) -> str:
    if error.status_code == 404 and "The route " in (error.body or ""):
        return "route_404"
    if error.status_code is not None:
        return f"http_{error.status_code}"
    return "client_error"


def _probe(command: ApiCommand, path: str, status: str) -> dict[str, str]:
    return {
        "action": command.action,
        "resource": command.resource,
        "method": command.method,
        "path": path,
        "status": status,
    }


def _query(command: ApiCommand) -> Query | None:
    if "bulk" in command.action:
        return (("ids[]", "0"),)
    return None


def _body(command: ApiCommand) -> JsonValue:
    return {} if command.accepts_body else None


def _headers(dry_run: bool) -> dict[str, str] | None:
    if dry_run:
        return {"X-Eramba-Swagger-Dry-Run": "1"}
    return None


def _path(command: ApiCommand, overrides: dict[str, str] | None = None) -> str:
    values = {
        parameter: (overrides or {}).get(parameter, _path_value(parameter))
        for parameter in command.path_params
    }
    return format_command_path(command, values)


def _path_value(parameter: str) -> str:
    if parameter.lower().endswith("id") or parameter.lower() == "id":
        return "0"
    if parameter == "modelAlias":
        return "Assets"
    if parameter == "field":
        return "file"
    return "x"


def _result_status(result: ApiResult) -> str:
    return "bytes" if isinstance(result, bytes) else "json"
