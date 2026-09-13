from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from erambactl._shared import jsonable_result as _jsonable
from erambactl.client import ErambaClient, ErambaError
from erambactl.commands import get_command
from erambactl.config import load_fleet, load_instance
from erambactl.types import JsonValue, Query

type SeedEntry = dict[str, object]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("examples/instances.json"))
    parser.add_argument("--fixture", type=Path, default=Path("examples/seed-data.json"))
    parser.add_argument("--instance")
    parser.add_argument("--all-instances", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    entries = _load_entries(args.fixture)
    if args.all_instances:
        report = _run_fleet(args.config, entries, args.dry_run)
    elif args.instance is not None:
        report = _run_instance(
            ErambaClient(load_instance(args.config, args.instance)),
            args.instance,
            entries,
            args.dry_run,
        )
    else:
        parser.error("Use --instance or --all-instances")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if _has_failures(report) else 0


def _load_entries(path: Path) -> tuple[SeedEntry, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw_entries = raw.get("commands")
    else:
        raw_entries = raw
    if not isinstance(raw_entries, list):
        raise TypeError("Seed fixture must be a list or an object with a commands list")
    return tuple(_entry(item) for item in raw_entries)


def _entry(raw: object) -> SeedEntry:
    if not isinstance(raw, dict):
        raise TypeError("Seed command must be an object")
    return cast(SeedEntry, raw)


def _run_fleet(path: Path, entries: tuple[SeedEntry, ...], dry_run: bool) -> dict[str, object]:
    fleet = load_fleet(path)
    reports = tuple(
        _run_instance(fleet.client(name), name, entries, dry_run) for name in fleet.names()
    )
    return {
        "instances": reports,
        "total_instances": len(reports),
        "failures": sum(cast(int, report["failures"]) for report in reports),
    }


def _run_instance(
    client: ErambaClient, name: str, entries: tuple[SeedEntry, ...], dry_run: bool
) -> dict[str, object]:
    results = tuple(_run_entry(client, entry, dry_run) for entry in entries)
    return {
        "instance": name,
        "total": len(results),
        "results": results,
        "failures": sum(1 for result in results if result["status"] == "error"),
    }


def _run_entry(client: ErambaClient, entry: SeedEntry, dry_run: bool) -> dict[str, object]:
    try:
        command = get_command(
            _string(entry, "action"),
            group=_string(entry, "group", "api-v2"),
            resource=_optional_string(entry, "resource"),
        )
        result = client.run(
            command,
            path_params=_string_dict(entry, "path_params"),
            query=_query(entry.get("query")),
            body=cast(JsonValue, entry.get("body")),
            headers={"X-Eramba-Swagger-Dry-Run": "1"} if dry_run else None,
        )
    except (ErambaError, OSError, TimeoutError, TypeError, ValueError) as error:
        return {"action": str(entry.get("action", "")), "status": "error", "error": str(error)}
    return {"action": command.action, "status": "ok", "result": _jsonable(result)}


def _string(entry: SeedEntry, key: str, default: str | None = None) -> str:
    value = entry.get(key, default)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value


def _optional_string(entry: SeedEntry, key: str) -> str | None:
    value = entry.get(key)
    if value is None or isinstance(value, str):
        return value
    raise TypeError(f"{key} must be a string")


def _string_dict(entry: SeedEntry, key: str) -> dict[str, str]:
    value = entry.get(key, {})
    if not isinstance(value, dict) or not all(
        isinstance(name, str) and isinstance(item, str) for name, item in value.items()
    ):
        raise TypeError(f"{key} must be an object with string values")
    return cast(dict[str, str], value)


def _query(value: object) -> Query | None:
    if value is None:
        return None
    if isinstance(value, dict) and all(
        isinstance(name, str) and isinstance(item, str) for name, item in value.items()
    ):
        return cast(dict[str, str], value)
    raise TypeError("query must be an object with string values")


def _has_failures(report: dict[str, object]) -> bool:
    return cast(int, report["failures"]) > 0
