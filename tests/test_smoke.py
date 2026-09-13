from __future__ import annotations

from tests.helpers import (
    API_COMMANDS,
    BEARER_VALUE,
    CHECK,
    ApiCommand,
    ErambaClient,
    ErambaError,
    ErambaInstance,
    JsonHandler,
    MissingRouteHandler,
    Path,
    ThreadingHTTPServer,
    _commands,
    _config,
    _error_status,
    _has_failures,
    _path,
    _safe_get_commands,
    _summary,
    cast,
    contextlib,
    find_commands,
    io,
    json,
    pytest,
    run_smoke,
    smoke_body,
    smoke_main,
    smoke_pairs,
    smoke_query,
    tempfile,
    threading,
)


def test_smoke_runs_json_bytes_and_http_error_commands() -> None:
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
            report = run_smoke(
                client,
                "test",
                (
                    ApiCommand(
                        "api", "get-assets-index", "assets", "GET", "/laravel/api/assets/index"
                    ),
                    ApiCommand(
                        "api",
                        "get-attachments-download",
                        "attachments",
                        "GET",
                        "/laravel/api/attachments/{id}/download",
                        ("id",),
                    ),
                    ApiCommand("api", "get-missing", "missing", "GET", "/missing"),
                ),
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(report["results"], {"json": 1, "bytes": 1, "http_404": 1})
    CHECK.assertEqual(report["failures"], [])
    CHECK.assertEqual(len(cast(list[dict[str, str]], report["http_errors"])), 1)
    CHECK.assertEqual(
        [probe["status"] for probe in cast(list[dict[str, str]], report["probes"])],
        ["json", "bytes", "http_404"],
    )


def test_smoke_classifies_missing_routes_separately() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            report = run_smoke(
                ErambaClient(
                    ErambaInstance(
                        name="test",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    )
                ),
                "test",
                (ApiCommand("api-v2", "get-assets-index", "assets", "GET", "/route-missing"),),
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(report["results"], {"route_404": 1})
    CHECK.assertEqual(cast(list[dict[str, str]], report["probes"])[0]["status"], "route_404")
    CHECK.assertTrue(_has_failures(report))


def test_smoke_fails_on_method_mismatch_status() -> None:
    report = {
        "instance": "test",
        "total": 1,
        "results": {"http_405": 1},
        "probes": [],
        "http_errors": [{"error": "method"}],
        "failures": [],
    }

    CHECK.assertTrue(_has_failures(report))


def test_smoke_classifies_client_error_status() -> None:
    CHECK.assertEqual(_error_status(ErambaError("boom")), "client_error")


def test_smoke_can_send_dry_run_header() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            report = run_smoke(
                ErambaClient(
                    ErambaInstance(
                        name="test",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                    )
                ),
                "test",
                (
                    ApiCommand(
                        "api",
                        "get-assets-bulk-update-get",
                        "assets",
                        "GET",
                        "/laravel/api/assets/index",
                    ),
                ),
                dry_run=True,
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(report["results"], {"json": 1})


def test_smoke_reports_client_failures() -> None:
    report = run_smoke(
        ErambaClient(ErambaInstance(name="test", base_url="file:///tmp/x", token=BEARER_VALUE)),
        "test",
        (ApiCommand("api", "get-assets-index", "assets", "GET", "/laravel/api/assets/index"),),
    )

    CHECK.assertEqual(report["results"], {"ValueError": 1})
    CHECK.assertEqual(len(cast(list[dict[str, str]], report["failures"])), 1)
    CHECK.assertEqual(
        cast(list[dict[str, str]], report["probes"])[0]["path"],
        "/laravel/api/assets/index",
    )


def test_smoke_summary_keeps_counts_without_probe_details() -> None:
    report = {
        "instance": "test",
        "total": 2,
        "results": {"json": 1, "http_404": 1},
        "probes": [{"status": "json"}, {"status": "http_404"}],
        "http_errors": [{"error": "missing"}],
        "failures": [],
    }

    CHECK.assertEqual(
        _summary(report),
        {
            "instance": "test",
            "total": 2,
            "results": {"json": 1, "http_404": 1},
            "http_errors": 1,
            "failures": 0,
        },
    )


def test_smoke_summary_keeps_fleet_counts_without_probe_details() -> None:
    fleet_report = {
        "instances": (
            {
                "instance": "local-a",
                "total": 1,
                "results": {"json": 1},
                "probes": [{"status": "json"}],
                "http_errors": [],
                "failures": [],
            },
        ),
        "total_instances": 1,
        "failures": [],
    }

    CHECK.assertEqual(
        _summary(fleet_report),
        {
            "instances": (
                {
                    "instance": "local-a",
                    "total": 1,
                    "results": {"json": 1},
                    "http_errors": 0,
                    "failures": 0,
                },
            ),
            "total_instances": 1,
            "failures": 0,
        },
    )


def test_smoke_builds_dummy_path_values_and_selects_commands() -> None:
    command = ApiCommand(
        "api",
        "post-attachments-store-form-create",
        "attachments",
        "POST",
        "/laravel/api/attachments/form-add/{modelAlias}/{field}/{custom}",
        ("modelAlias", "field", "custom"),
        True,
    )

    CHECK.assertEqual(_path(command), "/laravel/api/attachments/form-add/Assets/file/x")
    CHECK.assertEqual(
        _path(command, {"modelAlias": "Risks", "field": "attachment"}),
        "/laravel/api/attachments/form-add/Risks/attachment/x",
    )
    CHECK.assertEqual(smoke_body(command), {})
    CHECK.assertIsNone(smoke_body(API_COMMANDS[0]))
    CHECK.assertEqual(
        smoke_query(ApiCommand("api", "get-assets-bulk-update-get", "assets", "GET", "/x")),
        (("ids[]", "0"),),
    )
    CHECK.assertEqual(_commands(True, 1), API_COMMANDS[:1])
    CHECK.assertEqual(_commands(False, 1), _safe_get_commands()[:1])
    CHECK.assertEqual(
        _commands(True, 2, offset=1, method="get", resource="app-notifications"),
        tuple(
            command
            for command in API_COMMANDS
            if command.method == "GET" and command.resource == "app-notifications"
        )[1:3],
    )
    CHECK.assertEqual(_commands(True, 1, group="api-v2"), tuple(find_commands(group="api-v2"))[:1])
    CHECK.assertFalse(
        any(
            command.method == "DELETE" for command in _commands(True, None, skip_methods=["delete"])
        )
    )
    with pytest.raises(ValueError, match="limit"):
        _commands(True, -1)
    with pytest.raises(ValueError, match="offset"):
        _commands(True, None, offset=-1)


def test_smoke_parses_path_value_pairs() -> None:
    CHECK.assertEqual(
        smoke_pairs(["id=7", "modelAlias=Users"], "path value"),
        {"id": "7", "modelAlias": "Users"},
    )

    with pytest.raises(ValueError, match="Invalid path value"):
        smoke_pairs(["id"], "path value")


def test_smoke_main_prints_empty_report() -> None:
    stream = io.StringIO()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {"instances": {"local-a": {"base_url": "https://localhost", "token": BEARER_VALUE}}}
            )
        )

        with contextlib.redirect_stdout(stream):
            code = smoke_main(
                [
                    "--config",
                    str(path),
                    "--instance",
                    "local-a",
                    "--all",
                    "--method",
                    "post",
                    "--resource",
                    "assets",
                    "--offset",
                    "1",
                    "--limit",
                    "0",
                    "--path-value",
                    "id=7",
                ]
            )

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(json.loads(stream.getvalue())["total"], 0)
    CHECK.assertEqual(json.loads(stream.getvalue())["probes"], [])


def test_smoke_main_returns_error_for_route_metadata_failures(tmp_path: Path) -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), MissingRouteHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            path = _config(
                tmp_path,
                f"http://127.0.0.1:{server.server_port}",
                f"http://127.0.0.1:{server.server_port}",
            )
            with contextlib.redirect_stdout(stream):
                code = smoke_main(
                    [
                        "--config",
                        str(path),
                        "--instance",
                        "local-a",
                        "--all",
                        "--group",
                        "api-v2",
                        "--limit",
                        "1",
                        "--summary-only",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(json.loads(stream.getvalue())["results"], {"route_404": 1})


def test_smoke_main_returns_error_for_fleet_route_metadata_failures(tmp_path: Path) -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), MissingRouteHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            path = _config(
                tmp_path,
                f"http://127.0.0.1:{server.server_port}",
                f"http://127.0.0.1:{server.server_port}",
            )
            with contextlib.redirect_stdout(stream):
                code = smoke_main(
                    [
                        "--config",
                        str(path),
                        "--all-instances",
                        "--all",
                        "--group",
                        "api-v2",
                        "--limit",
                        "1",
                        "--summary-only",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(
        report,
        {
            "failures": 0,
            "instances": [
                {
                    "failures": 0,
                    "http_errors": 1,
                    "instance": "local-a",
                    "results": {"route_404": 1},
                    "total": 1,
                },
                {
                    "failures": 0,
                    "http_errors": 1,
                    "instance": "local-b",
                    "results": {"route_404": 1},
                    "total": 1,
                },
            ],
            "total_instances": 2,
        },
    )


def test_smoke_main_can_run_all_instances_from_config() -> None:
    stream = io.StringIO()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-b": {"base_url": "https://two.example", "token": BEARER_VALUE},
                        "local-a": {"base_url": "https://one.example", "token": BEARER_VALUE},
                    }
                }
            )
        )

        with contextlib.redirect_stdout(stream):
            code = smoke_main(["--config", str(path), "--all-instances", "--all", "--limit", "0"])

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report["total_instances"], 2)
    CHECK.assertEqual([item["instance"] for item in report["instances"]], ["local-a", "local-b"])
    CHECK.assertEqual(report["failures"], [])


def test_smoke_main_can_print_summary_only_for_all_instances() -> None:
    stream = io.StringIO()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {"base_url": "https://one.example", "token": BEARER_VALUE},
                    }
                }
            )
        )

        with contextlib.redirect_stdout(stream):
            code = smoke_main(
                [
                    "--config",
                    str(path),
                    "--all-instances",
                    "--all",
                    "--limit",
                    "0",
                    "--summary-only",
                ]
            )

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report["total_instances"], 1)
    CHECK.assertEqual(report["failures"], 0)
    CHECK.assertNotIn("probes", report["instances"][0])


def test_smoke_main_requires_instance_selection() -> None:
    with pytest.raises(SystemExit):
        smoke_main(["--limit", "0"])
