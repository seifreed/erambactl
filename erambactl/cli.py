from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import TypeVar, cast, overload

from erambactl import cli_payload as _payloads
from erambactl._shared import jsonable_result as _jsonable_result
from erambactl._shared import pairs as _pairs
from erambactl.client import (
    ApiResult,
    ErambaClient,
    ErambaError,
    ErambaFleet,
    ErambaInstance,
    Query,
)
from erambactl.commands import API_COMMANDS, ApiCommand, find_commands, format_command_path
from erambactl.config import load_fleet, load_instance
from erambactl.types import AuthMode

_Namespace = TypeVar("_Namespace")
_body = _payloads.body
_body_fields = _payloads.body_fields
_field_dest = _payloads.field_dest
_field_flag = _payloads.field_flag
_field_type = _payloads.field_type
_file = _payloads.file_upload
_path_param_dest = _payloads.path_param_dest
_payload = _payloads.payload


class ErambaArgumentParser(argparse.ArgumentParser):
    @overload
    def parse_args(
        self,
        args: Iterable[str] | None = None,
        namespace: None = None,
    ) -> argparse.Namespace: ...

    @overload
    def parse_args(self, args: Iterable[str] | None, namespace: _Namespace) -> _Namespace: ...

    @overload
    def parse_args(self, *, namespace: _Namespace) -> _Namespace: ...

    def parse_args(
        self,
        args: Iterable[str] | None = None,
        namespace: object | None = None,
    ) -> object:
        parsed_args = None if args is None else tuple(args)
        parsed: object
        if namespace is None:
            parsed = super().parse_args(parsed_args)
        else:
            parsed = super().parse_args(parsed_args, namespace)
        command = getattr(parsed, "command", None)
        if isinstance(command, ApiCommand):
            try:
                _normalize_command_arguments(parsed, command)
            except ValueError as error:
                self.error(str(error))
        return parsed


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "catalog", False):
        catalog = _catalog(
            resource=args.resource,
            action=args.action,
            method=args.method,
            accepts_body=args.accepts_body,
            group=args.group,
        )
        _print_catalog(catalog, cast(str, args.format))
        return 0
    if not hasattr(args, "command") and not getattr(args, "login", False):
        parser.print_help()
        return 2
    try:
        if getattr(args, "all_instances", False):
            return _run_all(args)
        result = _run_single(args)
    except (ErambaError, OSError, TypeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if result is not None:
        _print_result(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    return _parser()


def instance_from_args(args: argparse.Namespace) -> ErambaInstance:
    return _instance(args)


def run_command(client: ErambaClient, command: ApiCommand, args: argparse.Namespace) -> ApiResult:
    return _run(client, command, args)


def _run_all(args: argparse.Namespace) -> int:
    report, failed = _run_fleet(_fleet(args), args)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failed else 0


def _run_single(args: argparse.Namespace) -> ApiResult | None:
    client = ErambaClient(instance_from_args(args))
    if getattr(args, "login", False):
        print(client.session_cookie())
        return None
    return run_command(client, cast(ApiCommand, args.command), args)


def _parser() -> argparse.ArgumentParser:
    parser = ErambaArgumentParser(prog="erambactl")
    _add_instance_options(parser)
    subparsers = parser.add_subparsers(dest="group")
    _add_catalog_parser(subparsers)
    _add_login_parser(subparsers)
    _add_command_parsers(subparsers)
    return parser


def _add_instance_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path)
    parser.add_argument("--instance")
    parser.add_argument("--all-instances", action="store_true")
    parser.add_argument("--base-url")
    parser.add_argument("--token")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--cookie")
    parser.add_argument("--auth-mode", choices=("session", "basic"), default="session")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--insecure", action="store_true")


def _add_catalog_parser(
    subparsers: argparse._SubParsersAction[ErambaArgumentParser],
) -> None:
    catalog = subparsers.add_parser("commands")
    catalog.add_argument("--group")
    catalog.add_argument("--resource")
    catalog.add_argument("--action")
    catalog.add_argument("--method")
    catalog.add_argument("--accepts-body", choices=("yes", "no"))
    catalog.add_argument("--format", choices=("json", "text"), default="json")
    catalog.set_defaults(catalog=True)


def _add_login_parser(
    subparsers: argparse._SubParsersAction[ErambaArgumentParser],
) -> None:
    login = subparsers.add_parser("login")
    login.set_defaults(login=True)


def _add_command_parsers(
    subparsers: argparse._SubParsersAction[ErambaArgumentParser],
) -> None:
    groups: dict[str, argparse._SubParsersAction[ErambaArgumentParser]] = {}
    for command in API_COMMANDS:
        group = subparsers.choices.get(command.group)
        if group is None:
            group = subparsers.add_parser(command.group)
            groups[command.group] = group.add_subparsers(dest="action")
        action = groups[command.group].add_parser(command.action, usage=_command_usage(command))
        action.add_argument(
            "arguments", nargs="*", metavar="argument", help=_arguments_help(command)
        )
        for parameter in command.path_params:
            action.add_argument(
                _field_flag(parameter),
                dest=_path_param_dest(parameter),
                default=argparse.SUPPRESS,
                metavar=parameter,
            )
        if command.accepts_body:
            _add_body_arguments(action, command)
        action.add_argument("--dry-run", action="store_true")
        action.add_argument("--query", action="append", default=[])
        action.add_argument("--header", action="append", default=[])
        action.set_defaults(command=command)


def _add_body_arguments(parser: argparse.ArgumentParser, command: ApiCommand) -> None:
    body = parser.add_mutually_exclusive_group()
    body.add_argument("--data")
    body.add_argument("--data-file", type=Path)
    parser.add_argument("--form", action="append", default=[])
    parser.add_argument("--file", action="append", default=[])
    for field in _body_fields(command):
        parser.add_argument(
            _field_flag(field),
            dest=_field_dest(field),
            default=argparse.SUPPRESS,
            metavar=field,
            type=_field_type(command, field),
        )


def _normalize_command_arguments(args: object, command: ApiCommand) -> None:
    namespace = cast(argparse.Namespace, args)
    values = list(cast(list[str], namespace.arguments))
    if values and values[0] == command.resource:
        values.pop(0)
    named_values = {
        parameter: getattr(namespace, _path_param_dest(parameter))
        for parameter in command.path_params
        if hasattr(namespace, _path_param_dest(parameter))
    }
    if len(values) + len(named_values) != len(command.path_params):
        raise ValueError(f"Expected {len(command.path_params)} path parameters")
    namespace.resource = command.resource
    remaining_values = iter(values)
    for parameter in command.path_params:
        if parameter in named_values:
            setattr(namespace, parameter, named_values[parameter])
            continue
        setattr(namespace, parameter, next(remaining_values))


def _command_usage(command: ApiCommand) -> str:
    arguments = (f"[{command.resource}]", *command.path_params)
    return "%(prog)s " + " ".join(arguments)


def _arguments_help(command: ApiCommand) -> str:
    if command.path_params:
        return (
            f"path parameters: {', '.join(command.path_params)}; "
            f"optional legacy resource prefix: {command.resource}"
        )
    return f"optional legacy resource prefix: {command.resource}"


def _instance(args: argparse.Namespace) -> ErambaInstance:
    if args.config and args.instance:
        return load_instance(args.config, args.instance)
    if args.base_url and (args.token or args.cookie or (args.username and args.password)):
        return ErambaInstance(
            name=args.instance or "default",
            base_url=args.base_url,
            token=args.token,
            username=args.username,
            password=args.password,
            cookie=args.cookie,
            verify_tls=not args.insecure,
            auth_mode=cast(AuthMode, args.auth_mode),
            timeout=args.timeout,
        )
    raise ValueError("Use --config and --instance, or --base-url with token, cookie, or basic auth")


def _fleet(args: argparse.Namespace) -> ErambaFleet:
    if args.config is None:
        raise ValueError("Use --config with --all-instances")
    return load_fleet(args.config)


def _run_fleet(fleet: ErambaFleet, args: argparse.Namespace) -> tuple[dict[str, object], bool]:
    report: dict[str, object] = {}
    failed = False
    for name in fleet.names():
        client = fleet.client(name)
        try:
            if getattr(args, "login", False):
                report[name] = client.session_cookie()
            else:
                report[name] = _jsonable_result(_run(client, cast(ApiCommand, args.command), args))
        except (ErambaError, OSError, TypeError, ValueError) as error:
            report[name] = {"error": str(error)}
            failed = True
    return report, failed


def _run(client: ErambaClient, command: ApiCommand, args: argparse.Namespace) -> ApiResult:
    path = format_command_path(
        command,
        {parameter: getattr(args, parameter) for parameter in command.path_params},
    )
    query = _query(args.query)
    headers = _headers(args)
    body, form, files = _payload(args, command) if command.accepts_body else (None, None, ())
    return client.request(
        command.method,
        path,
        query=query,
        body=body,
        form=form,
        files=files,
        headers=headers or None,
    )


def _print_result(result: ApiResult) -> None:
    if isinstance(result, bytes):
        stream = getattr(sys.stdout, "buffer", None)
        if stream is None:
            sys.stdout.write(result.decode())
            return
        stream.write(result)
        return
    print(json.dumps(result, indent=2, sort_keys=True))


def _query(values: list[str]) -> Query:
    return _pairs(values, "query parameter")


def _headers(args: argparse.Namespace) -> dict[str, str]:
    headers = dict(_pairs(args.header, "header"))
    if args.dry_run:
        headers["X-Eramba-Swagger-Dry-Run"] = "1"
    return headers


def _catalog(
    resource: str | None = None,
    action: str | None = None,
    method: str | None = None,
    accepts_body: str | None = None,
    group: str | None = None,
) -> list[dict[str, object]]:
    body_filter = None if accepts_body is None else accepts_body == "yes"
    return [
        {
            "action": command.action,
            "accepts_body": command.accepts_body,
            "group": command.group,
            "method": command.method,
            "path": command.path,
            "path_params": list(command.path_params),
            "body_fields": list(_body_fields(command)),
            "resource": command.resource,
        }
        for command in find_commands(
            group=group,
            resource=resource,
            action=action,
            method=method,
            accepts_body=body_filter,
        )
    ]


def _print_catalog(catalog: list[dict[str, object]], output_format: str) -> None:
    if output_format == "text":
        for row in catalog:
            params = " ".join(cast(list[str], row["path_params"]))
            command = f"{row['group']} {row['action']}"
            suffix = f" {params}" if params else ""
            print(f"{command}{suffix}\t{row['method']}\t{row['path']}")
        return
    print(json.dumps(catalog, indent=2, sort_keys=True))
