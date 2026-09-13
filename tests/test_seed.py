from __future__ import annotations

from tests.helpers import (
    BEARER_VALUE,
    CHECK,
    ErambaClient,
    ErambaInstance,
    JsonHandler,
    Path,
    ThreadingHTTPServer,
    _config,
    _load_entries,
    cast,
    contextlib,
    io,
    json,
    pytest,
    seed_jsonable,
    seed_main,
    seed_query,
    seed_run_entry,
    threading,
)


def test_seed_runs_fixture_across_all_configured_instances(tmp_path: Path) -> None:
    fixture = tmp_path / "seed.json"
    fixture.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "group": "api-v2",
                        "action": "put-settings-authentication",
                        "body": {"connection_type": "default"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            config = _config(
                tmp_path,
                f"http://127.0.0.1:{server.server_port}",
                f"http://127.0.0.1:{server.server_port}",
            )
            with contextlib.redirect_stdout(stream):
                code = seed_main(
                    ["--config", str(config), "--fixture", str(fixture), "--all-instances"]
                )
        finally:
            server.shutdown()
            thread.join()

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report["failures"], 0)
    CHECK.assertEqual(report["total_instances"], 2)
    CHECK.assertEqual(report["instances"][0]["results"][0]["status"], "ok")


def test_seed_runs_fixture_for_one_instance_with_dry_run(tmp_path: Path) -> None:
    fixture = tmp_path / "seed.json"
    fixture.write_text(
        json.dumps(
            [
                {
                    "group": "api-v2",
                    "action": "put-settings-authentication",
                    "body": {"connection_type": "default"},
                }
            ]
        ),
        encoding="utf-8",
    )
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            config = _config(
                tmp_path,
                f"http://127.0.0.1:{server.server_port}",
                f"http://127.0.0.1:{server.server_port}",
            )
            with contextlib.redirect_stdout(stream):
                code = seed_main(
                    [
                        "--config",
                        str(config),
                        "--fixture",
                        str(fixture),
                        "--instance",
                        "local-a",
                        "--dry-run",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report["results"][0]["result"]["dry_run"], "1")


def test_seed_returns_failure_for_invalid_seed_command(tmp_path: Path) -> None:
    fixture = tmp_path / "seed.json"
    fixture.write_text(json.dumps([{"group": "api-v2", "action": "missing"}]), encoding="utf-8")
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            config = _config(
                tmp_path,
                f"http://127.0.0.1:{server.server_port}",
                f"http://127.0.0.1:{server.server_port}",
            )
            with contextlib.redirect_stdout(stream):
                code = seed_main(
                    ["--config", str(config), "--fixture", str(fixture), "--instance", "local-a"]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(json.loads(stream.getvalue())["failures"], 1)


def test_seed_rejects_invalid_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "seed.json"
    fixture.write_text(json.dumps({"commands": {}}), encoding="utf-8")

    with pytest.raises(TypeError, match="commands list"):
        _load_entries(fixture)


def test_seed_requires_instance_or_all_instances(tmp_path: Path) -> None:
    fixture = tmp_path / "seed.json"
    fixture.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(SystemExit):
        seed_main(["--fixture", str(fixture)])


def test_seed_rejects_non_object_command(tmp_path: Path) -> None:
    fixture = tmp_path / "seed.json"
    fixture.write_text(json.dumps(["bad"]), encoding="utf-8")

    with pytest.raises(TypeError, match="Seed command"):
        _load_entries(fixture)


def test_seed_reports_invalid_entry_fields() -> None:
    client = ErambaClient(
        ErambaInstance(name="test", base_url="http://127.0.0.1", token=BEARER_VALUE)
    )

    resource = seed_run_entry(client, {"action": "get-assets-index", "resource": 7}, False)
    path_params = seed_run_entry(
        client,
        {"action": "get-assets-index", "path_params": {"id": 7}},
        False,
    )
    query = seed_run_entry(client, {"action": "get-assets-index", "query": {"id": 7}}, False)
    action = seed_run_entry(client, {"action": 7}, False)

    CHECK.assertEqual(resource["status"], "error")
    CHECK.assertIn("resource", cast(str, resource["error"]))
    CHECK.assertEqual(path_params["status"], "error")
    CHECK.assertIn("path_params", cast(str, path_params["error"]))
    CHECK.assertEqual(query["status"], "error")
    CHECK.assertIn("query", cast(str, query["error"]))
    CHECK.assertEqual(action["status"], "error")
    CHECK.assertIn("action", cast(str, action["error"]))


def test_seed_query_and_binary_result_helpers() -> None:
    CHECK.assertIsNone(seed_query(None))
    CHECK.assertEqual(seed_query({"page": "1"}), {"page": "1"})
    CHECK.assertEqual(seed_jsonable(b"raw"), {"bytes": 3})
