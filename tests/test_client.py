from __future__ import annotations

from tests.helpers import (
    BEARER_VALUE,
    CHECK,
    COOKIE_VALUE,
    FAILED_LOGIN_VALUE,
    NO_COOKIE_VALUE,
    SESSION_COOKIE_VALUE,
    XSRF_COOKIE_VALUE,
    Any,
    ApiCommand,
    ErambaClient,
    ErambaError,
    ErambaFleet,
    ErambaInstance,
    JsonHandler,
    Path,
    ThreadingHTTPServer,
    UploadFile,
    _instance,
    _parser,
    cast,
    json,
    pytest,
    tempfile,
    threading,
)


def test_client_sends_json_requests_and_parses_responses() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )

            listed = client.request(
                "GET",
                "/laravel/api/assets/index",
                query={"page": "2"},
                headers={"X-Trace": "client"},
            )
            created = client.request("POST", "/laravel/api/assets/create", body={"name": "CRM"})
            deleted = client.request("DELETE", "/laravel/api/assets/delete/7")
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(
        listed,
        {
            "method": "GET",
            "auth": f"Bearer {BEARER_VALUE}",
            "cookie": None,
            "trace": "client",
        },
    )
    CHECK.assertEqual(created, {"method": "POST", "body": {"name": "CRM"}})
    CHECK.assertIsNone(deleted)


def test_client_can_skip_tls_verification_for_local_eramba() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                    verify_tls=False,
                )
            )

            result = client.request("GET", "/laravel/api/assets/index", query={"page": "2"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertIsInstance(result, dict)
    result_map = cast(dict[str, Any], result)
    CHECK.assertEqual(result_map["auth"], f"Bearer {BEARER_VALUE}")
    CHECK.assertIsNone(result_map["cookie"])
    CHECK.assertIsNone(result_map["trace"])


def test_client_can_use_basic_auth() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    username="user",
                    password=BEARER_VALUE,
                    auth_mode="basic",
                )
            )

            result = client.request("GET", "/laravel/api/assets/index", query={"page": "2"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(
        result,
        {
            "method": "GET",
            "auth": "Basic dXNlcjpiZWFyZXItdmFsdWU=",
            "cookie": None,
            "trace": None,
        },
    )


def test_client_can_login_with_session_credentials() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    username="user",
                    password=BEARER_VALUE,
                )
            )

            result = client.request("GET", "/laravel/api/assets/index", query={"page": "2"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(
        result,
        {
            "method": "GET",
            "auth": None,
            "cookie": f"{SESSION_COOKIE_VALUE}; translation=1",
            "trace": None,
        },
    )


def test_client_primes_xsrf_for_session_write_requests() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    username="user",
                    password=BEARER_VALUE,
                )
            )

            result = client.request("POST", "/laravel/api/program-scopes/create", body={})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(
        result,
        {
            "body": {},
            "cookie": f"{SESSION_COOKIE_VALUE}; translation=1; {XSRF_COOKIE_VALUE}",
            "xsrf": "encoded=",
        },
    )


def test_client_requires_credentials_for_login_command() -> None:
    client = ErambaClient(
        ErambaInstance(name="test", base_url="https://localhost", token=BEARER_VALUE)
    )

    with pytest.raises(ValueError, match="username and password"):
        client.session_cookie()


def test_client_rejects_login_without_session_cookie() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    username="user",
                    password=NO_COOKIE_VALUE,
                )
            )

            with pytest.raises(ErambaError, match="session cookie"):
                client.session_cookie()
        finally:
            server.shutdown()
            thread.join()


def test_client_rejects_failed_session_login() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    username="user",
                    password=FAILED_LOGIN_VALUE,
                )
            )

            with pytest.raises(ErambaError, match="Login failed"):
                client.session_cookie()
        finally:
            server.shutdown()
            thread.join()


def test_client_can_use_session_cookie() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    cookie=COOKIE_VALUE,
                )
            )

            result = client.request("GET", "/laravel/api/assets/index", query={"page": "2"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(
        result, {"method": "GET", "auth": None, "cookie": COOKIE_VALUE, "trace": None}
    )


def test_client_can_send_multipart_form_files() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "note.txt"
        path.write_text("hello", encoding="utf-8")
        with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                client = ErambaClient(
                    ErambaInstance(
                        name="test",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    )
                )

                result = client.request(
                    "POST",
                    "/laravel/api/attachments/form-add/Assets/file",
                    form={"name": "Evidence"},
                    files=(UploadFile("file", path),),
                )
            finally:
                server.shutdown()
                thread.join()

    CHECK.assertIsInstance(result, dict)
    result_map = cast(dict[str, Any], result)
    body = cast(str, result_map["body"])
    CHECK.assertTrue(str(result_map["content_type"]).startswith("multipart/form-data"))
    CHECK.assertIn('name="name"', body)
    CHECK.assertIn("Evidence", body)
    CHECK.assertIn('name="file"; filename="note.txt"', body)
    CHECK.assertIn("hello", body)


def test_client_escapes_multipart_names_and_rejects_header_breaks() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'quo"te.txt'
        path.write_text("hello", encoding="utf-8")
        with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                client = ErambaClient(
                    ErambaInstance(
                        name="test",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    )
                )

                result = client.request(
                    "POST",
                    "/laravel/api/attachments/form-add/Assets/file",
                    form={'na"me': "Evidence"},
                    files=(UploadFile('fi"le', path),),
                )
            finally:
                server.shutdown()
                thread.join()

    CHECK.assertIsInstance(result, dict)
    body = cast(str, cast(dict[str, Any], result)["body"])
    CHECK.assertIn(r'name="na\"me"', body)
    CHECK.assertIn(r'name="fi\"le"; filename="quo\"te.txt"', body)

    client = ErambaClient(
        ErambaInstance(name="test", base_url="https://example", token=BEARER_VALUE)
    )
    with pytest.raises(ValueError, match="Invalid multipart field"):
        client.request("POST", "/x", form={"bad\r\nname": "x"})
    with pytest.raises(ValueError, match="Invalid HTTP header name"):
        client.request("GET", "/x", headers={"X-Test\r\nInjected": "yes"})
    with pytest.raises(ValueError, match="Invalid HTTP header name"):
        client.request("GET", "/x", headers={"": "empty"})
    with pytest.raises(ValueError, match="Invalid HTTP header value"):
        client.request("GET", "/x", headers={"X-Test": "ok\r\nInjected: yes"})
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        client.request("GET\r\nInjected: yes", "/x")
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        client.request("", "/x")
    with pytest.raises(ValueError, match="Invalid HTTP method"):
        client.request("BAD METHOD", "/x")
    with pytest.raises(ValueError, match="Invalid multipart filename"):
        client.request("POST", "/x", files=(UploadFile("file", Path("bad\r\nname.txt")),))


def test_client_returns_non_json_responses_as_bytes() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )

            result = client.request("GET", "/laravel/api/attachments/1/download")
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(result, b"%PDF-1.7")


def test_client_preserves_repeated_query_parameters() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )

            result = client.request(
                "GET",
                "/laravel/api/assets/index",
                query=(("ids[]", "1"), ("ids[]", "2")),
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(result, {"query": "ids%5B%5D=1&ids%5B%5D=2"})


def test_client_runs_api_command_metadata() -> None:
    command = ApiCommand(
        "api",
        "get-assets-view",
        "assets",
        "GET",
        "/laravel/api/assets/view/{id}",
        ("id",),
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )

            result = client.run(command, path_params={"id": "7"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(result, {"id": 7})


def test_client_run_rejects_missing_path_parameters() -> None:
    client = ErambaClient(
        ErambaInstance(name="test", base_url="https://localhost", token=BEARER_VALUE)
    )
    command = ApiCommand(
        "api",
        "get-assets-view",
        "assets",
        "GET",
        "/laravel/api/assets/view/{id}",
        ("id",),
    )

    with pytest.raises(ValueError, match="id"):
        client.run(command)


def test_client_rejects_mixed_json_and_multipart_payloads() -> None:
    client = ErambaClient(
        ErambaInstance(name="test", base_url="https://localhost", token=BEARER_VALUE)
    )

    with pytest.raises(ValueError, match="Use JSON body or multipart form"):
        client.request("POST", "/laravel/api/assets/create", body={}, form={"name": "CRM"})


def test_instance_requires_authentication() -> None:
    with pytest.raises(ValueError, match="Use token, cookie, or username and password"):
        ErambaInstance(name="test", base_url="https://localhost:8443")


def test_instance_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        ErambaInstance(name="", base_url="https://localhost:8443", token=BEARER_VALUE)


def test_instance_rejects_unsafe_base_url() -> None:
    with pytest.raises(ValueError, match="base_url must not be empty"):
        ErambaInstance(name="test", base_url="", token=BEARER_VALUE)
    ErambaInstance(name="test", base_url="http://localhost:8080", token=BEARER_VALUE)
    ErambaInstance(name="test", base_url="http://[::1]:8080", token=BEARER_VALUE)
    with pytest.raises(ValueError, match="http base_url is only allowed for localhost"):
        ErambaInstance(name="test", base_url="http://eramba.example", token=BEARER_VALUE)
    with pytest.raises(ValueError, match="base_url must not contain whitespace"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443\r\nHost: evil.example",
            token=BEARER_VALUE,
        )
    with pytest.raises(ValueError, match="base_url must not contain whitespace"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443/api path",
            token=BEARER_VALUE,
        )


def test_instance_rejects_empty_credentials() -> None:
    empty = ""
    with pytest.raises(ValueError, match="token must not be empty"):
        ErambaInstance(name="test", base_url="https://localhost:8443", token=empty)
    with pytest.raises(ValueError, match="cookie must not be empty"):
        ErambaInstance(name="test", base_url="https://localhost:8443", cookie=empty)
    with pytest.raises(ValueError, match="username must not be empty"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            username="",
            password=BEARER_VALUE,
        )
    with pytest.raises(ValueError, match="password must not be empty"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            username="user",
            password=empty,
        )


def test_instance_rejects_unknown_auth_mode() -> None:
    with pytest.raises(ValueError, match="auth_mode"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            token=BEARER_VALUE,
            auth_mode=cast(Any, "digest"),
        )


def test_instance_rejects_invalid_verify_tls() -> None:
    with pytest.raises(TypeError, match="verify_tls"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            token=BEARER_VALUE,
            verify_tls=cast(Any, "false"),
        )


def test_instance_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError, match="timeout"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            token=BEARER_VALUE,
            timeout=0,
        )
    with pytest.raises(TypeError, match="timeout"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            token=BEARER_VALUE,
            timeout=True,
        )
    with pytest.raises(ValueError, match="timeout"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            token=BEARER_VALUE,
            timeout=float("nan"),
        )
    with pytest.raises(ValueError, match="timeout"):
        ErambaInstance(
            name="test",
            base_url="https://localhost:8443",
            token=BEARER_VALUE,
            timeout=float("inf"),
        )


def test_client_raises_clear_http_errors() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="test",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )

            with pytest.raises(ErambaError, match="404") as caught:
                client.request("GET", "/missing")
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(caught.value.status_code, 404)
    CHECK.assertEqual(caught.value.reason, "Not Found")
    CHECK.assertIn("missing", caught.value.body or "")


def test_client_rejects_non_http_urls() -> None:
    client = ErambaClient(
        ErambaInstance(name="test", base_url="file:///tmp/eramba", token=BEARER_VALUE)
    )
    valid = ErambaClient(
        ErambaInstance(name="test", base_url="https://eramba.example", token=BEARER_VALUE)
    )
    hostless = ErambaClient(
        ErambaInstance(name="test", base_url="https:///eramba", token=BEARER_VALUE)
    )

    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        client.request("GET", "/laravel/api/assets/index")
    with pytest.raises(ValueError, match="base_url must include a host"):
        hostless.request("GET", "/laravel/api/assets/index")
    with pytest.raises(ValueError, match="Request path must be relative"):
        valid.request("GET", "https://other.example/laravel/api/assets/index")
    with pytest.raises(ValueError, match="Request path must be relative"):
        valid.request("GET", "//other.example/laravel/api/assets/index")
    with pytest.raises(ValueError, match="Request path must not contain whitespace"):
        valid.request("GET", "/laravel/api/assets/index\r\nHost: evil.example")
    with pytest.raises(ValueError, match="Request path must not contain whitespace"):
        valid.request("GET", "/laravel/api/assets index")


def test_fleet_routes_requests_to_named_instances() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            fleet = ErambaFleet(
                (
                    ErambaInstance(
                        name="local-a",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    ),
                )
            )

            result = fleet.request(
                "local-a",
                "GET",
                "/laravel/api/assets/index",
                query={"page": "2"},
                headers={"X-Trace": "fleet"},
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(
        result,
        {
            "method": "GET",
            "auth": f"Bearer {BEARER_VALUE}",
            "cookie": None,
            "trace": "fleet",
        },
    )
    CHECK.assertEqual(fleet.names(), ("local-a",))


def test_fleet_rejects_duplicate_instance_names() -> None:
    instance = ErambaInstance(name="same", base_url="https://one.example", token=BEARER_VALUE)

    with pytest.raises(ValueError, match="Duplicate instance name: same"):
        ErambaFleet((instance, instance))


def test_fleet_routes_requests_to_all_instances() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            fleet = ErambaFleet(
                (
                    ErambaInstance(
                        name="local-a",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    ),
                    ErambaInstance(
                        name="local-b",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    ),
                )
            )

            result = fleet.request_all("GET", "/laravel/api/assets/index")
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(result, {"local-a": {"method": "GET"}, "local-b": {"method": "GET"}})


def test_fleet_runs_api_command_metadata() -> None:
    command = ApiCommand(
        "api",
        "get-assets-view",
        "assets",
        "GET",
        "/laravel/api/assets/view/{id}",
        ("id",),
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            fleet = ErambaFleet(
                (
                    ErambaInstance(
                        name="local-a",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    ),
                )
            )

            result = fleet.run("local-a", command, path_params={"id": "7"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(result, {"id": 7})


def test_fleet_runs_api_command_metadata_on_all_instances() -> None:
    command = ApiCommand(
        "api",
        "get-assets-view",
        "assets",
        "GET",
        "/laravel/api/assets/view/{id}",
        ("id",),
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            fleet = ErambaFleet(
                (
                    ErambaInstance(
                        name="local-a",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    ),
                    ErambaInstance(
                        name="local-b",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    ),
                )
            )

            result = fleet.run_all(command, path_params={"id": "7"})
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(result, {"local-a": {"id": 7}, "local-b": {"id": 7}})


def test_fleet_rejects_unknown_instances() -> None:
    fleet = ErambaFleet(())

    with pytest.raises(ValueError, match="Instance not found"):
        fleet.client("missing")


def test_instance_arguments_can_use_config_file() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {"base_url": "https://localhost:8443", "token": BEARER_VALUE}
                    }
                }
            )
        )
        args = _parser().parse_args(
            ["--config", str(path), "--instance", "local-a", "api", "get-assets-index", "assets"]
        )

        instance = _instance(args)

    CHECK.assertEqual(instance.base_url, "https://localhost:8443")
    CHECK.assertEqual(instance.token, BEARER_VALUE)
