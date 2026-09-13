from __future__ import annotations

import argparse
import json
import multiprocessing
from dataclasses import dataclass
from multiprocessing.queues import Queue
from typing import cast

from erambactl._shared import add_check_arguments, command_window, error_summary, pair_dict
from erambactl.cli import build_parser, instance_from_args
from erambactl.cli import run_command as cli_run
from erambactl.cli_payload import body_fields, field_flag
from erambactl.client import ErambaClient, ErambaError, ErambaInstance
from erambactl.commands import API_COMMANDS, ApiCommand
from erambactl.config import load_fleet, load_instance
from erambactl.real_cli_values import _field_value, _path_value, _real_values

_LAST_ACTIONS = {
    "post-settings-reset-database",
    "post-settings-reset-application-id",
}


@dataclass(frozen=True, slots=True)
class _Target:
    name: str
    argv: tuple[str, ...]
    values: dict[str, str]


def main(argv: list[str] | None = None) -> int:
    parser = _real_check_parser()
    args = parser.parse_args(argv)
    if not args.all_instances and args.instance is None:
        parser.error("Use --instance or --all-instances")

    try:
        report = _run(args, _targets(args), _commands(args))
    except (ErambaError, OSError, TypeError, ValueError) as error:
        report = _failure_report(error)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["failures"] else 0


def _real_check_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    add_check_arguments(parser)
    parser.add_argument("--action")
    parser.add_argument("--skip-action", action="append", default=[])
    parser.add_argument("--real-values", action="store_true")
    parser.add_argument("--strict-http", action="store_true")
    parser.add_argument("--request-timeout", type=float)
    return parser


def _failure_report(error: BaseException) -> dict[str, object]:
    return {
        "total": 0,
        "results": {"failure": 1},
        "failures": [{"error": error_summary(error)}],
    }


def _commands(args: argparse.Namespace) -> tuple[ApiCommand, ...]:
    skipped = {item.upper() for item in cast(list[str], args.skip_method)}
    skipped_actions = set(cast(list[str], getattr(args, "skip_action", [])))
    action = cast(str | None, getattr(args, "action", None))
    commands = tuple(
        command
        for command in API_COMMANDS
        if (args.group is None or command.group == args.group)
        and (action is None or command.action == action)
        and (args.method is None or command.method == args.method.upper())
        and (args.resource is None or command.resource == args.resource)
        and command.method not in skipped
        and command.action not in skipped_actions
    )
    ordered = tuple(sorted(commands, key=lambda command: command.action in _LAST_ACTIONS))
    return command_window(ordered, args.limit, args.offset)


def _run(
    args: argparse.Namespace, targets: tuple[_Target, ...], commands: tuple[ApiCommand, ...]
) -> dict[str, object]:
    parser = build_parser()
    path_values = pair_dict(cast(list[str], args.path_value), "path value")
    results: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    for target in targets:
        for command in commands:
            status, error = _call_cli(parser, _command_argv(args, target, command, path_values))
            results[status] = results.get(status, 0) + 1
            if _is_failure(args, status):
                failures.append(
                    {
                        "instance": target.name,
                        "action": command.action,
                        "resource": command.resource,
                        "status": status,
                        "error": error,
                    }
                )
    return {"total": len(commands) * len(targets), "results": results, "failures": failures}


def _call_cli(parser: argparse.ArgumentParser, argv: list[str]) -> tuple[str, str]:
    args = parser.parse_args(argv)
    timeout = cast(float, args.timeout)
    context = multiprocessing.get_context("spawn")
    results: Queue[tuple[str, str]] = context.Queue()
    process = context.Process(target=_call_parsed_cli, args=(args, results))
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join()
        results.close()
        return "failure", f"Timed out after {timeout:g} seconds"
    result = ("failure", "Command failed") if process.exitcode else results.get()
    results.close()
    return result


def _call_parsed_cli(args: argparse.Namespace, results: Queue[tuple[str, str]]) -> None:
    try:
        client = ErambaClient(instance_from_args(args))
        cli_run(client, cast(ApiCommand, args.command), args)
    except ErambaError as error:
        results.put((_error_status(error), error_summary(error)))
        return
    except (OSError, TypeError, ValueError) as error:
        results.put(("failure", error_summary(error)))
        return
    results.put(("ok", ""))


def _command_argv(
    args: argparse.Namespace, target: _Target, command: ApiCommand, path_values: dict[str, str]
) -> list[str]:
    argv = list(target.argv)
    argv.extend([command.group, command.action])
    for parameter in command.path_params:
        argv.extend(
            [
                field_flag(parameter),
                path_values.get(parameter, _path_value(command, target, parameter)),
            ]
        )
    if args.dry_run:
        argv.append("--dry-run")
    if command.action == "get-authorizations-index":
        argv.extend(["--query", "group=10"])
    if "bulk" in command.action:
        argv.extend(["--query", "ids[]=0"])
    if command.accepts_body:
        fields = body_fields(command)
        if fields:
            for field in fields:
                argv.extend([field_flag(field), _field_value(command, field)])
        else:
            argv.extend(["--data", "{}"])
    return argv


def _targets(args: argparse.Namespace) -> tuple[_Target, ...]:
    if args.all_instances:
        fleet = load_fleet(args.config)
        return tuple(_target(args, load_instance(args.config, name)) for name in fleet.names())
    return (_target(args, load_instance(args.config, cast(str, args.instance))),)


def _target(args: argparse.Namespace, instance: ErambaInstance) -> _Target:
    request_timeout = cast(float | None, args.request_timeout)
    timeout = instance.timeout if request_timeout is None else request_timeout
    instance = ErambaInstance(
        name=instance.name,
        base_url=instance.base_url,
        token=instance.token,
        username=instance.username,
        password=instance.password,
        cookie=instance.cookie,
        verify_tls=instance.verify_tls,
        auth_mode=instance.auth_mode,
        timeout=timeout,
    )
    client = ErambaClient(instance)
    values = _real_values(client) if args.real_values else {}
    argv = ["--base-url", instance.base_url, "--timeout", str(timeout)]
    if not instance.verify_tls:
        argv.append("--insecure")
    if instance.token is not None:
        argv.extend(["--token", instance.token])
    elif instance.cookie is not None:
        argv.extend(["--cookie", instance.cookie])
    else:
        argv.extend(["--cookie", client.session_cookie()])
    return _Target(instance.name, tuple(argv), values)


def _error_status(error: ErambaError) -> str:
    if error.status_code == 404 and "The route " in (error.body or ""):
        return "route_404"
    if error.status_code is not None:
        return f"http_{error.status_code}"
    return "failure"


def _is_failure(args: argparse.Namespace, status: str) -> bool:
    return status in {"failure", "route_404"} or (args.strict_http and status != "ok")
