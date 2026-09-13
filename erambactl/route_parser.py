from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from pathlib import Path

from erambactl.route_data import ROUTES

RouteTuple = tuple[str, str, str, str, tuple[str, ...], bool]

_NAME_RE = re.compile(r"->name\(\s*'(?P<name>[^']+)'\s*\)")
_PARAM_RE = re.compile(r"{(?P<name>[^}/]+)}")
_ROUTE_RE = re.compile(
    r"Route::(?P<method>get|post|put|patch|delete)\(\s*'(?P<uri>[^']+)'(?P<tail>.*)",
    re.IGNORECASE,
)
_WORD_BOUNDARY_RE = re.compile(r"([a-z0-9])([A-Z])")
_NON_WORD_RE = re.compile(r"[^A-Za-z0-9]+")


def parse_routes(source: str) -> tuple[RouteTuple, ...]:
    routes: list[RouteTuple] = []
    seen: dict[str, int] = {}
    for line in source.splitlines():
        match = _ROUTE_RE.search(line)
        if match is None:
            continue
        route = _route_from_match(match)
        count = seen.get(route[0], 0) + 1
        seen[route[0]] = count
        if count > 1:
            route = (f"{route[0]}-{count}", *route[1:])
        routes.append(route)
    return tuple(routes)


def route_data_difference(source: str) -> str | None:
    parsed = parse_routes(source)
    if len(parsed) != len(ROUTES):
        return f"route count mismatch: catalog has {len(ROUTES)}, parsed {len(parsed)}"
    return _first_route_difference(parsed)


def _first_route_difference(parsed: Sequence[RouteTuple]) -> str | None:
    for index, (expected, actual) in enumerate(zip(ROUTES, parsed, strict=True), start=1):
        if expected != actual:
            return f"route mismatch at {index}: catalog {expected!r}, parsed {actual!r}"
    return None


def render_route_data(routes: Sequence[RouteTuple]) -> str:
    lines = [
        "from __future__ import annotations",
        "",
        "ROUTES: tuple[tuple[str, str, str, str, tuple[str, ...], bool], ...] = (",
    ]
    for action, resource, method, path, path_params, accepts_body in routes:
        lines.extend(
            (
                "    (",
                f"        {_quote(action)},",
                f"        {_quote(resource)},",
                f"        {_quote(method)},",
                f"        {_quote(path)},",
                f"        {_format_params(path_params)},",
                f"        {accepts_body},",
                "    ),",
            )
        )
    lines.append(")")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse eramba Laravel API routes.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--print", action="store_true", dest="print_routes")
    args = parser.parse_args(argv)

    source = args.path.read_text(encoding="utf-8")
    routes = parse_routes(source)
    if args.print_routes:
        print(render_route_data(routes), end="")
        return 0

    difference = route_data_difference(source)
    if difference is not None:
        print(difference)
        return 1
    print(f"route catalog matches {len(routes)} routes")
    return 0


def _route_from_match(match: re.Match[str]) -> RouteTuple:
    method = match.group("method").upper()
    uri = match.group("uri")
    normalized_uri = f"/{uri.lstrip('/')}"
    name_match = _NAME_RE.search(match.group("tail"))
    action_source = (
        name_match.group("name") if name_match is not None else normalized_uri.strip("/")
    )
    resource = _slug(normalized_uri.strip("/").split("/", maxsplit=1)[0])
    return (
        f"{method.lower()}-{_slug(action_source)}",
        resource,
        method,
        f"/laravel/api{normalized_uri}",
        tuple(_PARAM_RE.findall(normalized_uri)),
        method != "GET",
    )


def _slug(value: str) -> str:
    split = _WORD_BOUNDARY_RE.sub(r"\1-\2", value)
    return _NON_WORD_RE.sub("-", split).strip("-").lower()


def _format_params(path_params: tuple[str, ...]) -> str:
    if not path_params:
        return "()"
    values = ", ".join(_quote(value) for value in path_params)
    if len(path_params) == 1:
        values = f"{values},"
    return f"({values})"


def _quote(value: str) -> str:
    return json.dumps(value)
