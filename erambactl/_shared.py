from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from erambactl.types import ApiResult


def pairs(values: list[str], label: str) -> tuple[tuple[str, str], ...]:
    result: list[tuple[str, str]] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid {label}: {value}")
        key, item = value.split("=", 1)
        result.append((key, item))
    return tuple(result)


def pair_dict(values: list[str], label: str) -> dict[str, str]:
    return dict(pairs(values, label))


def add_check_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=Path("examples/instances.json"))
    parser.add_argument("--instance")
    parser.add_argument("--all-instances", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--group")
    parser.add_argument("--method")
    parser.add_argument("--resource")
    parser.add_argument("--skip-method", action="append", default=[])
    parser.add_argument("--path-value", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")


def command_window[T](
    commands: Sequence[T],
    limit: int | None,
    offset: int = 0,
) -> tuple[T, ...]:
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")
    if offset < 0:
        raise ValueError("offset must be non-negative")
    return tuple(commands[offset:] if limit is None else commands[offset : offset + limit])


def jsonable_result(result: ApiResult) -> object:
    if isinstance(result, bytes):
        return {"bytes": len(result)}
    return result


def error_summary(error: BaseException) -> str:
    return str(error).splitlines()[0][:200]
