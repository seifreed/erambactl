from __future__ import annotations

import argparse
import contextlib
import io
import json
import multiprocessing
import os
import runpy
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast

import pytest

import erambactl
from erambactl._shared import jsonable_result as seed_jsonable
from erambactl._shared import pair_dict as smoke_pairs
from erambactl.api_v2_data import V2_ROUTES
from erambactl.api_v2_fields import V2_BODY_FIELDS
from erambactl.cli import (
    _body,
    _catalog,
    _file,
    _instance,
    _parser,
    _payload,
    _print_catalog,
    _print_result,
    _query,
    main,
)
from erambactl.client import ErambaClient, ErambaError, ErambaFleet, ErambaInstance, UploadFile
from erambactl.commands import (
    API_COMMANDS,
    API_GROUPS,
    API_RESOURCES,
    ApiCommand,
    find_commands,
    format_command_path,
    get_command,
)
from erambactl.config import load_fleet, load_instance
from erambactl.real_cli_check import _call_cli as real_cli_call_cli
from erambactl.real_cli_check import _call_parsed_cli as real_cli_call_parsed_cli
from erambactl.real_cli_check import _command_argv as real_cli_command_argv
from erambactl.real_cli_check import _commands as real_cli_commands
from erambactl.real_cli_check import _error_status as real_cli_error_status
from erambactl.real_cli_check import _is_failure as real_cli_is_failure
from erambactl.real_cli_check import _Target
from erambactl.real_cli_check import _target as real_cli_target
from erambactl.real_cli_check import main as real_cli_main
from erambactl.real_cli_values import _field_value as real_cli_field_value
from erambactl.real_cli_values import _find_id as real_cli_find_id
from erambactl.real_cli_values import _first_filter_id as real_cli_first_filter_id
from erambactl.real_cli_values import _first_item_id as real_cli_first_item_id
from erambactl.real_cli_values import _first_nested_id_value as real_cli_first_nested_id_value
from erambactl.real_cli_values import _path_value as real_cli_path_value
from erambactl.real_cli_values import _real_values as real_cli_real_values
from erambactl.route_data import ROUTES
from erambactl.route_parser import main as route_parser_main
from erambactl.route_parser import parse_routes, render_route_data, route_data_difference
from erambactl.seed import _load_entries
from erambactl.seed import _query as seed_query
from erambactl.seed import _run_entry as seed_run_entry
from erambactl.seed import main as seed_main
from erambactl.smoke import (
    _body as smoke_body,
)
from erambactl.smoke import (
    _commands,
    _error_status,
    _has_failures,
    _path,
    _safe_get_commands,
    _summary,
    run_smoke,
)
from erambactl.smoke import (
    _query as smoke_query,
)
from erambactl.smoke import (
    main as smoke_main,
)

BEARER_VALUE = "bearer-value"

ENV_NAME = "ERAMBA_AUTH_VALUE"

MISSING_ENV_NAME = "ERAMBA_AUTH_VALUE_MISSING"

BASIC_ENV_NAME = "ERAMBA_BASIC_AUTH_VALUE"

COOKIE_VALUE = "PHPSESSID=local-value"

SESSION_COOKIE_VALUE = "PHPSESSID=session-value"

XSRF_COOKIE_VALUE = "XSRF-TOKEN=encoded%3D"

NO_COOKIE_VALUE = "no-cookie"

FAILED_LOGIN_VALUE = "failed"

CHECK = unittest.TestCase()


class JsonHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/laravel/api/assets/index":
            self._write(200, {"method": "GET"}, cookies=[XSRF_COOKIE_VALUE])
            return
        if self.path == "/laravel/api/assets/view/7":
            self._write(200, {"id": 7})
            return
        if self.path in {
            "/laravel/api/attachments/0/download",
            "/laravel/api/attachments/1/download",
        }:
            self._write_bytes(200, b"%PDF-1.7", "application/pdf")
            return
        if self.path == "/laravel/api/assets/index?ids%5B%5D=1&ids%5B%5D=2":
            self._write(200, {"query": self.path.split("?", 1)[1]})
            return
        if self.path == "/laravel/api/assets/index?page=2":
            body = {
                "method": "GET",
                "auth": self.headers["Authorization"],
                "cookie": self.headers["Cookie"],
                "trace": self.headers["X-Trace"],
            }
            dry_run = self.headers.get("X-Eramba-Swagger-Dry-Run")
            if dry_run is not None:
                body["dry_run"] = dry_run
            self._write(200, body)
            return
        if self.path == "/laravel/api/assets/index?ids%5B%5D=0":
            self._write(
                200,
                {
                    "query": self.path.split("?", 1)[1],
                    "dry_run": self.headers.get("X-Eramba-Swagger-Dry-Run"),
                },
            )
            return
        if self.path == "/route-missing":
            self._write(
                404,
                {
                    "error": True,
                    "exception": "Symfony\\Component\\HttpKernel\\Exception\\NotFoundHttpException",
                    "message": "The route api/v2/assets/index could not be found.",
                },
            )
            return
        self._write(404, {"error": "missing"})

    def do_POST(self) -> None:
        size = int(self.headers["Content-Length"])
        raw_body = self.rfile.read(size)
        content_type = self.headers["Content-Type"]
        if self.path == "/system-api/login":
            body = json.loads(raw_body)
            login = body.get("login")
            password = body.get("password")
            if login == "user" and password == NO_COOKIE_VALUE:
                self._write(200, {"success": True})
                return
            if login == "user" and password == FAILED_LOGIN_VALUE:
                self._write(200, {"success": False})
                return
            status = 200 if login == "user" and password == BEARER_VALUE else 401
            self._write(
                status,
                {"success": status == 200},
                cookies=[SESSION_COOKIE_VALUE, "translation=1"],
            )
            return
        if self.path == "/laravel/api/program-scopes/create":
            self._write(
                201,
                {
                    "body": json.loads(raw_body),
                    "cookie": self.headers["Cookie"],
                    "xsrf": self.headers["X-XSRF-TOKEN"],
                },
            )
            return
        if content_type.startswith("multipart/form-data"):
            self._write(
                201,
                {
                    "method": "POST",
                    "content_type": content_type,
                    "body": raw_body.decode(),
                },
            )
            return
        body = json.loads(raw_body)
        self._write(201, {"method": "POST", "body": body})

    def do_PUT(self) -> None:
        size = int(self.headers["Content-Length"])
        raw_body = self.rfile.read(size)
        body = json.loads(raw_body)
        self._write(
            200,
            {
                "method": "PUT",
                "body": body,
                "dry_run": self.headers.get("X-Eramba-Swagger-Dry-Run"),
            },
        )

    def do_DELETE(self) -> None:
        self.send_response(204)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _write(self, status: int, body: dict[str, Any], cookies: list[str] | None = None) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        for cookie in cookies or []:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(payload)

    def _write_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class MissingRouteHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        payload = json.dumps(
            {
                "error": True,
                "message": "The route api/v2/assets/index could not be found.",
            }
        ).encode()
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


class RealValuesHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {
            "/laravel/api/assets/index",
            "/laravel/api/goals/index",
            "/laravel/api/activity-log/activity-logs/index/Assets",
            "/laravel/api/activity-log/activity-logs/archive/index/Assets",
            "/laravel/api/custom-dynamic-status/custom-dynamic-statuses/index/Assets",
            "/laravel/api/notifications/notification-system-items/index/Goals",
            "/laravel/api/translations/translations/index",
            "/empty",
        }:
            items = [] if self.path == "/empty" else [{"_id": 7}]
            self._write(200, {"success": True, "data": {"data": {"items": items}}})
            return
        if self.path == "/missing-id":
            self._write(200, {"success": True, "data": {"data": {"items": [{"name": "x"}]}}})
            return
        if self.path == "/laravel/api/filters/Assets/index":
            self._write(
                200,
                {
                    "success": True,
                    "data": {"filters": [{"id": 8, "user_id": 1, "model": "Assets"}]},
                },
            )
            return
        if self.path == "/laravel/api/app-notifications/list":
            self._write(
                200, {"success": True, "data": {"app_notifications": {"data": [{"id": 9}]}}}
            )
            return
        if self.path == "/laravel/api/visualisation-settings":
            self._write(200, {"success": True, "data": {"Program": {"items": [{"_id": 10}]}}})
            return
        self._write(404, {"error": "missing"})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _write(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class FilterFallbackHandler(RealValuesHandler):
    def do_GET(self) -> None:
        if self.path == "/laravel/api/filters/Assets/index":
            self._write(200, {"success": True, "data": {"filters": [{"id": 11}]}})
            return
        super().do_GET()


class FilterWithoutIdHandler(RealValuesHandler):
    def do_GET(self) -> None:
        if self.path == "/laravel/api/filters/Assets/index":
            self._write(
                200,
                {"success": True, "data": {"filters": [{"user_id": 1, "model": "Assets"}]}},
            )
            return
        super().do_GET()


class NotificationFailureHandler(RealValuesHandler):
    def do_GET(self) -> None:
        if self.path == "/laravel/api/notifications/notification-system-items/index/Goals":
            self._write(500, {"error": "server"})
            return
        super().do_GET()


class NotificationMissingIdHandler(RealValuesHandler):
    def do_GET(self) -> None:
        if self.path == "/laravel/api/notifications/notification-system-items/index/Goals":
            self._write(200, {"success": True, "data": {"data": {"items": [{"name": "x"}]}}})
            return
        super().do_GET()


class SlowHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        time.sleep(0.2)
        payload = json.dumps({"success": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


def _route_source_from_catalog() -> str:
    lines = []
    for action, _resource, method, path, _path_params, _accepts_body in ROUTES:
        uri = path.removeprefix("/laravel/api")
        action_source = action.removeprefix(f"{method.lower()}-")
        lines.append(
            f"Route::{method.lower()}('{uri}', [RouteDataController::class, 'call'])->name('{action_source}');"
        )
    return "\n".join(lines)


def _config(tmp_path: Path, local_a_url: str, local_b_url: str) -> Path:
    path = tmp_path / "instances.json"
    path.write_text(
        json.dumps(
            {
                "instances": {
                    "local-b": {"base_url": local_b_url, "token": BEARER_VALUE},
                    "local-a": {"base_url": local_a_url, "token": BEARER_VALUE},
                }
            }
        ),
        encoding="utf-8",
    )
    return path


__all__ = [
    "API_COMMANDS",
    "API_GROUPS",
    "API_RESOURCES",
    "BASIC_ENV_NAME",
    "BEARER_VALUE",
    "CHECK",
    "COOKIE_VALUE",
    "ENV_NAME",
    "FAILED_LOGIN_VALUE",
    "MISSING_ENV_NAME",
    "NO_COOKIE_VALUE",
    "SESSION_COOKIE_VALUE",
    "V2_BODY_FIELDS",
    "V2_ROUTES",
    "XSRF_COOKIE_VALUE",
    "Any",
    "ApiCommand",
    "ErambaClient",
    "ErambaError",
    "ErambaFleet",
    "ErambaInstance",
    "FilterFallbackHandler",
    "FilterWithoutIdHandler",
    "JsonHandler",
    "MissingRouteHandler",
    "NotificationFailureHandler",
    "NotificationMissingIdHandler",
    "Path",
    "RealValuesHandler",
    "SlowHandler",
    "ThreadingHTTPServer",
    "UploadFile",
    "_Target",
    "_body",
    "_catalog",
    "_commands",
    "_config",
    "_error_status",
    "_file",
    "_has_failures",
    "_instance",
    "_load_entries",
    "_parser",
    "_path",
    "_payload",
    "_print_catalog",
    "_print_result",
    "_query",
    "_route_source_from_catalog",
    "_safe_get_commands",
    "_summary",
    "argparse",
    "cast",
    "contextlib",
    "erambactl",
    "find_commands",
    "format_command_path",
    "get_command",
    "io",
    "json",
    "load_fleet",
    "load_instance",
    "main",
    "multiprocessing",
    "os",
    "parse_routes",
    "pytest",
    "real_cli_call_cli",
    "real_cli_call_parsed_cli",
    "real_cli_command_argv",
    "real_cli_commands",
    "real_cli_error_status",
    "real_cli_field_value",
    "real_cli_find_id",
    "real_cli_first_filter_id",
    "real_cli_first_item_id",
    "real_cli_first_nested_id_value",
    "real_cli_is_failure",
    "real_cli_main",
    "real_cli_path_value",
    "real_cli_real_values",
    "real_cli_target",
    "render_route_data",
    "route_data_difference",
    "route_parser_main",
    "run_smoke",
    "runpy",
    "seed_jsonable",
    "seed_main",
    "seed_query",
    "seed_run_entry",
    "smoke_body",
    "smoke_main",
    "smoke_pairs",
    "smoke_query",
    "sys",
    "tempfile",
    "threading",
]
