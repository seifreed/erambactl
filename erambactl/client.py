from __future__ import annotations

import json
import math
import ssl
from base64 import b64encode
from dataclasses import dataclass
from http.cookies import SimpleCookie
from ipaddress import ip_address
from urllib.error import HTTPError
from urllib.parse import unquote, urlencode, urljoin, urlparse
from urllib.request import HTTPSHandler, Request, build_opener

from erambactl._http import decode_response, request_data
from erambactl.commands import ApiCommand, format_command_path
from erambactl.types import ApiResult, AuthMode, JsonValue, Query, UploadFile

__all__ = [
    "ApiResult",
    "AuthMode",
    "ErambaClient",
    "ErambaError",
    "ErambaFleet",
    "ErambaInstance",
    "JsonValue",
    "Query",
    "UploadFile",
]

_HEADER_NAME_CHARS = frozenset(
    "!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)


@dataclass(frozen=True, slots=True)
class ErambaInstance:
    name: str
    base_url: str
    token: str | None = None
    username: str | None = None
    password: str | None = None
    cookie: str | None = None
    verify_tls: bool = True
    auth_mode: AuthMode = "session"
    timeout: float = 30.0

    def __post_init__(self) -> None:
        _reject_empty(self.name, "name")
        _reject_empty(self.base_url, "base_url")
        _reject_whitespace(self.base_url, "base_url")
        _reject_remote_http(self.base_url)
        _reject_empty(self.token, "token")
        _reject_empty(self.username, "username")
        _reject_empty(self.password, "password")
        _reject_empty(self.cookie, "cookie")
        has_bearer = self.token is not None
        has_credentials = self.username is not None and self.password is not None
        if not has_bearer and not has_credentials and self.cookie is None:
            raise ValueError("Use token, cookie, or username and password")
        if self.auth_mode not in {"session", "basic"}:
            raise ValueError("auth_mode must be session or basic")
        if not isinstance(self.verify_tls, bool):
            raise TypeError("verify_tls must be boolean")
        if not isinstance(self.timeout, int | float) or isinstance(self.timeout, bool):
            raise TypeError("timeout must be numeric")
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError("timeout must be greater than zero")


class ErambaError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        reason: str | None = None,
        body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
        self.body = body


def _reject_empty(value: str | None, name: str) -> None:
    if value == "":
        raise ValueError(f"{name} must not be empty")


def _reject_whitespace(value: str, name: str) -> None:
    if any(character.isspace() for character in value):
        raise ValueError(f"{name} must not contain whitespace")


def _reject_remote_http(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname == "localhost":
        return
    try:
        if ip_address(parsed.hostname or "").is_loopback:
            return
    except ValueError:
        pass
    raise ValueError("http base_url is only allowed for localhost")


class ErambaClient:
    def __init__(self, instance: ErambaInstance) -> None:
        self.instance = instance
        self._cookie = instance.cookie

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        body: JsonValue = None,
        form: dict[str, str] | None = None,
        files: tuple[UploadFile, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> ApiResult:
        method = _validated_method(method)
        url = self._url(path, query)
        request_headers = self._headers(method)
        if headers is not None:
            request_headers.update(headers)
        data, content_type = request_data(body, form, files)
        if content_type is not None:
            request_headers["Content-Type"] = content_type
        payload, cookies, content_type = self._read(
            Request(url, data=data, headers=_validated_headers(request_headers), method=method)
        )
        self._update_cookie(cookies)
        return decode_response(payload, content_type)

    def run(
        self,
        command: ApiCommand,
        *,
        path_params: dict[str, str] | None = None,
        query: Query | None = None,
        body: JsonValue = None,
        form: dict[str, str] | None = None,
        files: tuple[UploadFile, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> ApiResult:
        return self.request(
            command.method,
            format_command_path(command, path_params or {}),
            query=query,
            body=body,
            form=form,
            files=files,
            headers=headers,
        )

    def session_cookie(self) -> str:
        if self._cookie is None:
            self._login()
        if self._cookie is None:
            raise ErambaError("Login did not return a session cookie")
        return self._cookie

    def _auth_header(self) -> str | None:
        if self.instance.token is not None:
            return f"Bearer {self.instance.token}"
        if (
            self.instance.auth_mode != "basic"
            or self.instance.username is None
            or self.instance.password is None
        ):
            return None
        raw = f"{self.instance.username}:{self.instance.password}".encode()
        return f"Basic {b64encode(raw).decode()}"

    def _headers(self, method: str) -> dict[str, str]:
        headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
        auth_header = self._auth_header()
        if auth_header is not None:
            headers["Authorization"] = auth_header
        if self._cookie is not None:
            headers["Cookie"] = self._cookie
        elif self._uses_session_login():
            headers["Cookie"] = self.session_cookie()
        if _needs_xsrf(method) and self._cookie is not None:
            token = _cookie_value(self._cookie, "XSRF-TOKEN")
            if token is None:
                self._prime_xsrf(self._cookie)
                token = _cookie_value(self._cookie, "XSRF-TOKEN")
            if token is not None:
                headers["Cookie"] = self._cookie
                headers["X-XSRF-TOKEN"] = unquote(token)
        return headers

    def _login(self) -> None:
        if self.instance.username is None or self.instance.password is None:
            raise ValueError("Use username and password for session login")
        body = json.dumps(
            {"login": self.instance.username, "password": self.instance.password}
        ).encode()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        payload, cookies, _content_type = self._read(
            Request(self._url("/system-api/login"), data=body, headers=headers, method="POST")
        )
        result = json.loads(payload) if payload else {}
        if not isinstance(result, dict) or result.get("success") is not True:
            raise ErambaError("Login failed")
        self._update_cookie(cookies)

    def _prime_xsrf(self, cookie: str) -> None:
        _payload, cookies, _content_type = self._read(
            Request(
                self._url("/laravel/api/assets/index"),
                headers={
                    "Accept": "application/json",
                    "Cookie": cookie,
                    "X-Requested-With": "XMLHttpRequest",
                },
                method="GET",
            )
        )
        self._update_cookie(cookies)

    def _read(self, request: Request) -> tuple[bytes, list[str], str]:
        context = (
            ssl.create_default_context() if self.instance.verify_tls else _unverified_context()
        )
        try:
            with build_opener(HTTPSHandler(context=context)).open(
                request, timeout=self.instance.timeout
            ) as response:
                return (
                    response.read(),
                    response.headers.get_all("Set-Cookie", []),
                    response.headers.get("Content-Type", ""),
                )
        except HTTPError as error:
            message = error.read().decode(errors="replace")
            raise ErambaError(
                f"{error.code} {error.reason}: {message}",
                status_code=error.code,
                reason=error.reason,
                body=message,
            ) from error

    def _update_cookie(self, headers: list[str]) -> None:
        cookie = _cookie_header(self._cookie, headers)
        if cookie is not None:
            self._cookie = cookie

    def _url(self, path: str, query: Query | None = None) -> str:
        if any(character.isspace() for character in path):
            raise ValueError("Request path must not contain whitespace")
        path_url = urlparse(path)
        if path_url.scheme or path_url.netloc:
            raise ValueError("Request path must be relative")
        url = urljoin(self.instance.base_url.rstrip("/") + "/", path.lstrip("/"))
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported URL scheme: {url}")
        if not parsed.netloc:
            raise ValueError("base_url must include a host")
        if query:
            return f"{url}?{urlencode(query)}"
        return url

    def _uses_session_login(self) -> bool:
        return (
            self.instance.token is None
            and self.instance.auth_mode == "session"
            and self.instance.username is not None
            and self.instance.password is not None
        )


class ErambaFleet:
    def __init__(self, instances: tuple[ErambaInstance, ...]) -> None:
        names = [instance.name for instance in instances]
        if len(names) != len(set(names)):
            duplicate = next(name for index, name in enumerate(names) if name in names[:index])
            raise ValueError(f"Duplicate instance name: {duplicate}")
        self._clients = {instance.name: ErambaClient(instance) for instance in instances}

    def names(self) -> tuple[str, ...]:
        return tuple(self._clients)

    def client(self, name: str) -> ErambaClient:
        try:
            return self._clients[name]
        except KeyError as error:
            raise ValueError(f"Instance not found: {name}") from error

    def request(
        self,
        instance: str,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        body: JsonValue = None,
        form: dict[str, str] | None = None,
        files: tuple[UploadFile, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> ApiResult:
        return self.client(instance).request(
            method,
            path,
            query=query,
            body=body,
            form=form,
            files=files,
            headers=headers,
        )

    def request_all(
        self,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        body: JsonValue = None,
        form: dict[str, str] | None = None,
        files: tuple[UploadFile, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> dict[str, ApiResult]:
        return {
            name: client.request(
                method,
                path,
                query=query,
                body=body,
                form=form,
                files=files,
                headers=headers,
            )
            for name, client in self._clients.items()
        }

    def run(
        self,
        instance: str,
        command: ApiCommand,
        *,
        path_params: dict[str, str] | None = None,
        query: Query | None = None,
        body: JsonValue = None,
        form: dict[str, str] | None = None,
        files: tuple[UploadFile, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> ApiResult:
        return self.client(instance).run(
            command,
            path_params=path_params,
            query=query,
            body=body,
            form=form,
            files=files,
            headers=headers,
        )

    def run_all(
        self,
        command: ApiCommand,
        *,
        path_params: dict[str, str] | None = None,
        query: Query | None = None,
        body: JsonValue = None,
        form: dict[str, str] | None = None,
        files: tuple[UploadFile, ...] = (),
        headers: dict[str, str] | None = None,
    ) -> dict[str, ApiResult]:
        return {
            name: client.run(
                command,
                path_params=path_params,
                query=query,
                body=body,
                form=form,
                files=files,
                headers=headers,
            )
            for name, client in self._clients.items()
        }


def _unverified_context() -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def _cookie_header(existing: str | None, headers: list[str]) -> str | None:
    if existing is None and not headers:
        return None
    cookies: SimpleCookie = SimpleCookie()
    if existing is not None:
        cookies.load(existing)
    for header in headers:
        cookies.load(header)
    return "; ".join(f"{name}={morsel.value}" for name, morsel in cookies.items())


def _cookie_value(header: str, name: str) -> str | None:
    cookies: SimpleCookie = SimpleCookie()
    cookies.load(header)
    morsel = cookies.get(name)
    return None if morsel is None else morsel.value


def _needs_xsrf(method: str) -> bool:
    return method.upper() not in {"GET", "HEAD", "OPTIONS"}


def _validated_method(method: str) -> str:
    method = method.upper()
    if not method or any(character not in _HEADER_NAME_CHARS for character in method):
        raise ValueError(f"Invalid HTTP method: {method!r}")
    return method


def _validated_headers(headers: dict[str, str]) -> dict[str, str]:
    for name, value in headers.items():
        if not name or any(character not in _HEADER_NAME_CHARS for character in name):
            raise ValueError(f"Invalid HTTP header name: {name!r}")
        if "\r" in value or "\n" in value:
            raise ValueError(f"Invalid HTTP header value for {name!r}")
    return headers
