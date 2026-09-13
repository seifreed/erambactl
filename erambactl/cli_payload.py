from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

from erambactl._shared import pairs
from erambactl.api_v2_fields import (
    V2_BODY_FIELDS,
    V2_DATA_WRAPPED_ACTIONS,
    V2_RAW_STRING_FIELDS,
)
from erambactl.commands import ApiCommand
from erambactl.types import JsonValue, UploadFile

type Payload = tuple[JsonValue, dict[str, str] | None, tuple[UploadFile, ...]]


def body(value: str | None, path: Path | None = None) -> JsonValue:
    raw = path.read_text(encoding="utf-8") if path else value
    if raw is None:
        raise ValueError("Use --data or --data-file")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise TypeError("--data must be a JSON object")
    return data


def payload(args: argparse.Namespace, command: ApiCommand | None = None) -> Payload:
    field_payload = field_body(args, command) if command is not None else {}
    if field_payload:
        if args.data is not None or args.data_file is not None or args.form or args.file:
            raise ValueError("Use endpoint field flags, JSON body, or multipart form, not together")
        return field_payload, None, ()
    if args.data is not None or args.data_file is not None:
        if args.form or args.file:
            raise ValueError("Use JSON body or multipart form, not both")
        return body(args.data, args.data_file), None, ()
    form = dict(pairs(args.form, "form field"))
    files = tuple(file_upload(value) for value in args.file)
    return None, form or None, files


def file_upload(value: str) -> UploadFile:
    if "=" not in value:
        raise ValueError(f"Invalid file field: {value}")
    field, path = value.split("=", 1)
    return UploadFile(field, Path(path))


def body_fields(command: ApiCommand) -> tuple[str, ...]:
    if command.group != "api-v2":
        return ()
    return V2_BODY_FIELDS.get(command.action, ())


def field_body(args: argparse.Namespace, command: ApiCommand) -> dict[str, JsonValue]:
    namespace = vars(args)
    field_payload = {
        field: cast(JsonValue, namespace[field_dest(field)])
        for field in body_fields(command)
        if field_dest(field) in namespace
    }
    if not field_payload:
        return {}
    if command.action in V2_DATA_WRAPPED_ACTIONS:
        return {"data": field_payload}
    return field_payload


def field_dest(field: str) -> str:
    return "api_field_" + "".join(character if character.isalnum() else "_" for character in field)


def field_flag(field: str) -> str:
    normalized = field.replace("_", "-")
    parts: list[str] = []
    for index, character in enumerate(normalized):
        previous = normalized[index - 1] if index > 0 else ""
        next_character = normalized[index + 1] if index + 1 < len(normalized) else ""
        if (
            character.isupper()
            and previous not in {"", "-"}
            and (previous.islower() or previous.isdigit() or next_character.islower())
        ):
            parts.append("-")
        parts.append(character.lower())
    return "--" + "".join(parts)


def field_type(command: ApiCommand, field: str) -> Callable[[str], JsonValue]:
    if field in V2_RAW_STRING_FIELDS.get(command.action, ()):
        return str
    return field_value


def path_param_dest(parameter: str) -> str:
    return "path_param_" + field_dest(parameter)


def field_value(value: str) -> JsonValue:
    try:
        return cast(JsonValue, json.loads(value))
    except json.JSONDecodeError:
        return value
