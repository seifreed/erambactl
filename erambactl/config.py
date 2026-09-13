from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, cast

from erambactl.client import ErambaFleet, ErambaInstance
from erambactl.types import AuthMode


def load_instance(path: Path, name: str) -> ErambaInstance:
    raw_instances = _raw_instances(path)
    if name not in raw_instances:
        raise ValueError(f"Instance not found: {name}")
    return _load_instance(name, raw_instances[name])


def load_fleet(path: Path) -> ErambaFleet:
    raw_instances = _raw_instances(path)
    return ErambaFleet(
        tuple(_load_instance(name, raw) for name, raw in sorted(raw_instances.items()))
    )


def _raw_instances(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("Invalid instances config")
    raw_instances = data.get("instances", {})
    if not isinstance(raw_instances, dict):
        raise TypeError("Invalid instances config")
    return raw_instances


def _load_instance(name: str, raw: Any) -> ErambaInstance:
    if not isinstance(raw, dict):
        raise TypeError(f"Invalid instance config: {name}")
    return ErambaInstance(
        name=name,
        base_url=_string(raw, "base_url"),
        token=_optional_secret(raw, "token", "token_env"),
        username=_optional_string(raw, "username"),
        password=_optional_secret(raw, "password", "password_env"),
        cookie=_optional_secret(raw, "cookie", "cookie_env"),
        verify_tls=_bool(raw, "verify_tls", True),
        auth_mode=cast(AuthMode, raw.get("auth_mode", "session")),
        timeout=_number(raw, "timeout", 30.0),
    )


def _optional_secret(raw: dict[str, Any], value_key: str, env_key: str) -> str | None:
    if value_key in raw:
        return _string(raw, value_key)
    if env_key not in raw:
        return None
    env_name = _string(raw, env_key)
    token = os.environ.get(env_name)
    if token is None:
        raise ValueError(f"Environment variable not set: {env_name}")
    return token


def _optional_string(raw: dict[str, Any], key: str) -> str | None:
    if key not in raw:
        return None
    return _string(raw, key)


def _string(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"Missing string config key: {key}")
    return value


def _number(raw: dict[str, Any], key: str, default: float) -> float:
    value = raw.get(key, default)
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise TypeError(f"Invalid numeric config key: {key}")
    return float(value)


def _bool(raw: dict[str, Any], key: str, default: bool) -> bool:
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise TypeError(f"Invalid boolean config key: {key}")
    return value
