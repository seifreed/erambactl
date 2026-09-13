from __future__ import annotations

import json
import mimetypes
import secrets
from typing import cast

from erambactl.types import ApiResult, JsonValue, UploadFile


def request_data(
    body: JsonValue,
    form: dict[str, str] | None,
    files: tuple[UploadFile, ...],
) -> tuple[bytes | None, str | None]:
    if body is not None and (form or files):
        raise ValueError("Use JSON body or multipart form, not both")
    if form or files:
        return _multipart(form or {}, files)
    if body is not None:
        return json.dumps(body).encode(), "application/json"
    return None, None


def decode_response(payload: bytes, content_type: str) -> ApiResult:
    if not payload:
        return None
    if "json" not in content_type.lower():
        return payload
    return cast(JsonValue, json.loads(payload))


def _multipart(form: dict[str, str], files: tuple[UploadFile, ...]) -> tuple[bytes, str]:
    boundary = f"erambactl-{secrets.token_hex(16)}"
    chunks: list[bytes] = []
    for key, value in form.items():
        name = _multipart_value(key, "field")
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )
    for upload in files:
        field = _multipart_value(upload.field, "field")
        filename = _multipart_value(upload.path.name, "filename")
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{field}"; ' f'filename="{filename}"\r\n'
                ).encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                upload.path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _multipart_value(value: str, label: str) -> str:
    if "\r" in value or "\n" in value:
        raise ValueError(f"Invalid multipart {label}: {value!r}")
    return value.replace("\\", "\\\\").replace('"', r"\"")
