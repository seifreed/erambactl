from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

type JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None
type ApiResult = JsonValue | bytes
type AuthMode = Literal["session", "basic"]
type Query = dict[str, str] | tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class UploadFile:
    field: str
    path: Path
