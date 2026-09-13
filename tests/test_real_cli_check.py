from __future__ import annotations

from tests.helpers import (
    BEARER_VALUE,
    CHECK,
    COOKIE_VALUE,
    SESSION_COOKIE_VALUE,
    ErambaClient,
    ErambaError,
    ErambaInstance,
    FilterFallbackHandler,
    FilterWithoutIdHandler,
    JsonHandler,
    MissingRouteHandler,
    NotificationFailureHandler,
    NotificationMissingIdHandler,
    Path,
    RealValuesHandler,
    SlowHandler,
    ThreadingHTTPServer,
    _config,
    _parser,
    _Target,
    argparse,
    contextlib,
    find_commands,
    get_command,
    io,
    json,
    multiprocessing,
    pytest,
    real_cli_call_cli,
    real_cli_call_parsed_cli,
    real_cli_command_argv,
    real_cli_commands,
    real_cli_error_status,
    real_cli_field_value,
    real_cli_find_id,
    real_cli_first_filter_id,
    real_cli_first_item_id,
    real_cli_first_nested_id_value,
    real_cli_is_failure,
    real_cli_main,
    real_cli_path_value,
    real_cli_real_values,
    real_cli_target,
    threading,
)


def test_real_cli_check_builds_endpoint_specific_cli_arguments() -> None:
    args = argparse.Namespace(
        config=Path("examples/instances.json"),
        instance="local-a",
        all_instances=False,
        dry_run=True,
    )
    command = get_command("post-filters", group="api-v2")

    argv = real_cli_command_argv(
        args,
        _Target("local-a", ("--base-url", "https://one.example", "--token", BEARER_VALUE), {}),
        command,
        {},
    )

    CHECK.assertEqual(argv[:4], ["--base-url", "https://one.example", "--token", BEARER_VALUE])
    CHECK.assertIn("--dry-run", argv)
    CHECK.assertIn("--name", argv)
    CHECK.assertIn("--model", argv)
    CHECK.assertIn("--params", argv)
    CHECK.assertEqual(real_cli_field_value(command, "params"), "{}")
    CHECK.assertEqual(real_cli_field_value(command, "group_id"), "10")
    CHECK.assertEqual(real_cli_field_value(command, "status"), "1")
    CHECK.assertEqual(real_cli_field_value(command, "view"), "[]")
    CHECK.assertEqual(real_cli_field_value(command, "customFields"), "{}")
    CHECK.assertEqual(real_cli_field_value(command, "review"), "2027-12-31")
    CHECK.assertEqual(real_cli_field_value(command, "code"), "return true;")
    CHECK.assertEqual(real_cli_field_value(command, "name"), "x")
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-assets-edit-id", group="api-v2"), "BusinessUnits"),
        "[1]",
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-assets-edit-id", group="api-v2"), "AssetOwners"),
        '["User-1"]',
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-assets-edit-id", group="api-v2"), "AssetMediaTypes"),
        "1",
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-assets-edit-id", group="api-v2"), "AssetLabels"),
        "null",
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-assets-edit-id", group="api-v2"), "Legals"),
        "[]",
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-goals-edit-id", group="api-v2"), "Owners"),
        '["User-1"]',
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-goals-edit-id", group="api-v2"), "Contacts"),
        '["User-1"]',
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-goals-edit-id", group="api-v2"), "status"),
        "current",
    )
    CHECK.assertEqual(
        real_cli_field_value(
            get_command("put-goals-edit-id", group="api-v2"), "audit_calendar_type"
        ),
        "0",
    )
    CHECK.assertEqual(
        real_cli_field_value(get_command("put-goals-edit-id", group="api-v2"), "Projects"),
        "[]",
    )
    CHECK.assertEqual(real_cli_field_value(command, "connection_type"), "default")
    CHECK.assertEqual(real_cli_field_value(command, "ldap_connector_id"), "null")
    CHECK.assertEqual(real_cli_field_value(command, "auth_awareness"), "0")
    CHECK.assertEqual(real_cli_field_value(command, "reset_db"), "1")
    CHECK.assertEqual(real_cli_field_value(command, "client_key"), "x")
    CHECK.assertEqual(real_cli_field_value(command, "test_email"), "admin@eramba.org")
    CHECK.assertEqual(real_cli_field_value(command, "EMAIL_NAME"), "erambactl")
    CHECK.assertEqual(real_cli_field_value(command, "PUBLIC_ADDRESS"), "https://localhost")
    CHECK.assertEqual(real_cli_field_value(command, "QUEUE_TRANSPORT_LIMIT"), "1")
    CHECK.assertEqual(real_cli_field_value(command, "SMTP_USE"), "0")
    CHECK.assertEqual(real_cli_field_value(command, "authorization"), "Assets")
    CHECK.assertEqual(real_cli_field_value(command, "authorizations"), '["Assets"]')
    CHECK.assertEqual(real_cli_field_value(command, "action"), "index")
    CHECK.assertEqual(real_cli_field_value(command, "permission"), "1")
    CHECK.assertEqual(
        real_cli_field_value(command, "elements"),
        '{"general":{"hidden":"0","position":"0","elements":{}}}',
    )
    CHECK.assertEqual(real_cli_field_value(command, "composer_packages"), "")
    CHECK.assertEqual(real_cli_field_value(command, "language"), "php")
    CHECK.assertEqual(real_cli_field_value(command, "timeout"), "30")
    CHECK.assertEqual(real_cli_field_value(command, "global"), "0")
    CHECK.assertEqual(real_cli_field_value(command, "team_id"), "1")

    path_command = get_command("put-assets-edit-id", group="api-v2")
    path_argv = real_cli_command_argv(args, _Target("local-a", (), {}), path_command, {"id": "9"})
    CHECK.assertIn("--id", path_argv)
    CHECK.assertIn("9", path_argv)

    bulk_command = get_command("get-program-scopes-bulk-update-get")
    CHECK.assertIn(
        "ids[]=0", real_cli_command_argv(args, _Target("local-a", (), {}), bulk_command, {})
    )

    empty_body_command = get_command("delete-filters-id", group="api-v2")
    CHECK.assertIn(
        "{}",
        real_cli_command_argv(args, _Target("local-a", (), {}), empty_body_command, {}),
    )
    CHECK.assertEqual(real_cli_path_value(command, _Target("local-a", (), {}), "id"), "0")
    CHECK.assertEqual(
        real_cli_path_value(command, _Target("local-a", (), {}), "modelAlias"), "Assets"
    )
    CHECK.assertEqual(real_cli_path_value(command, _Target("local-a", (), {}), "field"), "name")
    CHECK.assertEqual(
        real_cli_path_value(
            get_command("get-filters-model-alias-field-options-field", group="api-v2"),
            _Target("local-a", (), {}),
            "field",
        ),
        "asset_media_type_id",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command(
                "get-notifications-notification-system-items-index-model-alias",
                group="api-v2",
            ),
            _Target("local-a", (), {}),
            "modelAlias",
        ),
        "Goals",
    )
    CHECK.assertEqual(real_cli_path_value(command, _Target("local-a", (), {}), "model"), "Assets")
    CHECK.assertEqual(real_cli_path_value(command, _Target("local-a", (), {}), "custom"), "x")
    CHECK.assertEqual(
        real_cli_path_value(path_command, _Target("local-a", (), {"asset_id": "12"}), "id"),
        "12",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command("put-goals-edit-id", group="api-v2"),
            _Target("local-a", (), {"goal_id": "13"}),
            "id",
        ),
        "13",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command("put-app-notifications-id-view", group="api-v2"),
            _Target("local-a", (), {"app_notification_id": "14"}),
            "id",
        ),
        "14",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command("put-visualisation-settings-edit-status-id", group="api-v2"),
            _Target("local-a", (), {"visualisation_setting_id": "15"}),
            "id",
        ),
        "15",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command(
                "get-custom-dynamic-status-custom-dynamic-statuses-edit-status-enabled-id",
                group="api-v2",
            ),
            _Target("local-a", (), {"dynamic_status_id": "16"}),
            "id",
        ),
        "16",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command(
                "put-notifications-notification-system-items-edit-status-id", group="api-v2"
            ),
            _Target("local-a", (), {"notification_system_item_id": "17"}),
            "id",
        ),
        "17",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command("get-translations-translations-edit-status-id", group="api-v2"),
            _Target("local-a", (), {"translation_id": "18"}),
            "id",
        ),
        "18",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command(
                "get-activity-log-activity-logs-share-model-alias-activity-log-id",
                group="api-v2",
            ),
            _Target("local-a", (), {"activity_log_id": "19"}),
            "activityLogId",
        ),
        "19",
    )
    CHECK.assertEqual(
        real_cli_path_value(
            get_command(
                "get-activity-log-activity-logs-archive-share-model-alias-activity-log-id",
                group="api-v2",
            ),
            _Target("local-a", (), {"archived_activity_log_id": "20"}),
            "activityLogId",
        ),
        "20",
    )


def test_real_cli_check_selects_commands_and_classifies_errors() -> None:
    args = argparse.Namespace(
        group="api-v2",
        method="delete",
        resource=None,
        skip_method=[],
        offset=0,
        limit=1,
    )

    CHECK.assertEqual(
        real_cli_commands(args), tuple(find_commands(group="api-v2", method="delete"))[:1]
    )
    auth_index_argv = real_cli_command_argv(
        argparse.Namespace(dry_run=False),
        _Target("local-a", (), {}),
        get_command("get-authorizations-index", group="api-v2"),
        {},
    )
    CHECK.assertIn("group=10", auth_index_argv)
    filtered_args = argparse.Namespace(
        group="api-v2",
        action="post-settings-reset-database",
        method=None,
        resource=None,
        skip_method=[],
        skip_action=["post-settings-reset-database"],
        offset=0,
        limit=None,
    )
    CHECK.assertEqual(real_cli_commands(filtered_args), ())
    CHECK.assertEqual(real_cli_error_status(ErambaError("boom", status_code=422)), "http_422")
    CHECK.assertEqual(
        real_cli_error_status(
            ErambaError("missing", status_code=404, body="The route x could not be found")
        ),
        "route_404",
    )
    CHECK.assertEqual(real_cli_error_status(ErambaError("boom")), "failure")
    CHECK.assertFalse(real_cli_is_failure(argparse.Namespace(strict_http=False), "http_500"))
    CHECK.assertTrue(real_cli_is_failure(argparse.Namespace(strict_http=True), "http_500"))
    CHECK.assertTrue(real_cli_is_failure(argparse.Namespace(strict_http=False), "route_404"))
    with pytest.raises(ValueError, match="limit"):
        real_cli_commands(
            argparse.Namespace(
                group=None,
                action=None,
                method=None,
                resource=None,
                skip_method=[],
                skip_action=[],
                offset=0,
                limit=-1,
            )
        )
    with pytest.raises(ValueError, match="offset"):
        real_cli_commands(
            argparse.Namespace(
                group=None,
                action=None,
                method=None,
                resource=None,
                skip_method=[],
                skip_action=[],
                offset=-1,
                limit=None,
            )
        )


def test_real_cli_check_runs_real_cli_path_against_http_server(tmp_path: Path) -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            path = _config(
                tmp_path,
                f"http://127.0.0.1:{server.server_port}",
                f"http://127.0.0.1:{server.server_port}",
            )
            with contextlib.redirect_stdout(stream):
                code = real_cli_main(
                    [
                        "--config",
                        str(path),
                        "--all-instances",
                        "--group",
                        "api-v2",
                        "--resource",
                        "assets",
                        "--method",
                        "get",
                        "--offset",
                        "1",
                        "--limit",
                        "1",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report, {"failures": [], "results": {"ok": 2}, "total": 2})


def test_real_cli_check_reports_real_route_failures(tmp_path: Path) -> None:
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
                code = real_cli_main(
                    [
                        "--config",
                        str(path),
                        "--instance",
                        "local-a",
                        "--group",
                        "api-v2",
                        "--resource",
                        "assets",
                        "--method",
                        "get",
                        "--offset",
                        "1",
                        "--limit",
                        "1",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(report["results"], {"route_404": 1})
    CHECK.assertEqual(len(report["failures"]), 1)


def test_real_cli_check_targets_auth_modes_and_transport_failures() -> None:
    parser = _parser()
    command = get_command("get-assets-index", group="api-v2")
    target_args = argparse.Namespace(real_values=False, request_timeout=None)
    token_target = real_cli_target(
        target_args,
        ErambaInstance(
            name="token",
            base_url="http://127.0.0.1",
            token=BEARER_VALUE,
            verify_tls=False,
        ),
    )
    cookie_target = real_cli_target(
        target_args, ErambaInstance(name="cookie", base_url="http://127.0.0.1", cookie=COOKIE_VALUE)
    )
    timeout_target = real_cli_target(
        argparse.Namespace(real_values=False, request_timeout=5.0),
        ErambaInstance(name="timeout", base_url="http://127.0.0.1", cookie=COOKIE_VALUE),
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            session_target = real_cli_target(
                target_args,
                ErambaInstance(
                    name="session",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    username="user",
                    password=BEARER_VALUE,
                ),
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertIn("--token", token_target.argv)
    CHECK.assertIn("--insecure", token_target.argv)
    CHECK.assertIn("--cookie", cookie_target.argv)
    CHECK.assertIn("5.0", timeout_target.argv)
    CHECK.assertTrue(any(SESSION_COOKIE_VALUE in value for value in session_target.argv))
    with pytest.raises(ValueError, match="timeout"):
        real_cli_target(
            argparse.Namespace(real_values=False, request_timeout=0),
            ErambaInstance(name="timeout", base_url="http://127.0.0.1", cookie=COOKIE_VALUE),
        )
    CHECK.assertEqual(
        real_cli_call_cli(
            parser,
            [
                "--base-url",
                "ftp://127.0.0.1",
                "--token",
                BEARER_VALUE,
                "api-v2",
                command.action,
            ],
        )[0],
        "failure",
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), SlowHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            CHECK.assertEqual(
                ErambaClient(
                    ErambaInstance(
                        name="slow",
                        base_url=f"http://127.0.0.1:{server.server_port}",
                        token=BEARER_VALUE,
                        timeout=1,
                    )
                ).request("GET", "/laravel/api/assets/index"),
                {"success": True},
            )
            status, error = real_cli_call_cli(
                parser,
                [
                    "--base-url",
                    f"http://127.0.0.1:{server.server_port}",
                    "--timeout",
                    "0.01",
                    "--token",
                    BEARER_VALUE,
                    "api-v2",
                    command.action,
                ],
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(status, "failure")
    CHECK.assertEqual(error, "Timed out after 0.01 seconds")


def test_real_cli_check_worker_classifies_results() -> None:
    parser = _parser()
    command = get_command("get-assets-index", group="api-v2")
    context = multiprocessing.get_context("spawn")
    success_results = context.Queue()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            real_cli_call_parsed_cli(
                parser.parse_args(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api-v2",
                        command.action,
                    ]
                ),
                success_results,
            )
        finally:
            server.shutdown()
            thread.join()
    CHECK.assertEqual(success_results.get(timeout=1), ("ok", ""))
    success_results.close()

    failure_results = context.Queue()
    real_cli_call_parsed_cli(
        parser.parse_args(
            [
                "--base-url",
                "ftp://127.0.0.1",
                "--token",
                BEARER_VALUE,
                "api-v2",
                command.action,
            ]
        ),
        failure_results,
    )
    CHECK.assertEqual(failure_results.get(timeout=1)[0], "failure")
    failure_results.close()

    route_results = context.Queue()
    with ThreadingHTTPServer(("127.0.0.1", 0), MissingRouteHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            real_cli_call_parsed_cli(
                parser.parse_args(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api-v2",
                        command.action,
                    ]
                ),
                route_results,
            )
        finally:
            server.shutdown()
            thread.join()
    CHECK.assertEqual(route_results.get(timeout=1)[0], "route_404")
    route_results.close()


def test_real_cli_check_discovers_real_values_over_http() -> None:
    not_found = 0
    with ThreadingHTTPServer(("127.0.0.1", 0), RealValuesHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="real-values",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )
            values = real_cli_real_values(client)
            filter_id = real_cli_first_filter_id(client)
            item_id = real_cli_first_item_id(client, "/laravel/api/assets/index")
            nested_id = real_cli_first_nested_id_value({"data": [{"id": 21}]})
            missing = real_cli_find_id(b"bytes")
            try:
                client.request("GET", "/missing")
            except ErambaError as error:
                not_found = error.status_code or 0
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(values["asset_id"], "7")
    CHECK.assertEqual(values["filter_id"], "8")
    CHECK.assertEqual(values["app_notification_id"], "9")
    CHECK.assertEqual(values["visualisation_setting_id"], "10")
    CHECK.assertEqual(filter_id, "8")
    CHECK.assertEqual(item_id, "7")
    CHECK.assertEqual(nested_id, "21")
    CHECK.assertIsNone(missing)
    CHECK.assertEqual(not_found, 404)


def test_real_cli_check_discovers_filter_id_from_nested_fallback() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), FilterFallbackHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="real-values",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )
            filter_id = real_cli_first_filter_id(client)
            asset_id = real_cli_first_item_id(client, "/laravel/api/assets/index")
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(filter_id, "11")
    CHECK.assertEqual(asset_id, "7")


def test_real_cli_check_uses_seeded_notification_item_when_index_fails() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), NotificationFailureHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="real-values",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )
            values = real_cli_real_values(client)
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(values["notification_system_item_id"], "1")

    with ThreadingHTTPServer(("127.0.0.1", 0), NotificationMissingIdHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="real-values",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )
            values = real_cli_real_values(client)
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(values["notification_system_item_id"], "1")


def test_real_cli_check_rejects_missing_real_values() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), RealValuesHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="real-values",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )
            with pytest.raises(ValueError, match="No real data"):
                real_cli_first_item_id(client, "/empty")
            with pytest.raises(ValueError, match="No real id"):
                real_cli_first_item_id(client, "/missing-id")
            with pytest.raises(ValueError, match="No real id"):
                real_cli_first_nested_id_value({})
            with pytest.raises(ValueError, match="No real id"):
                real_cli_first_nested_id_value({"id": True})
            with pytest.raises(ValueError, match="No real id"):
                real_cli_first_nested_id_value({"id": ""})
            CHECK.assertEqual(real_cli_first_nested_id_value({"id": "12"}), "12")
        finally:
            server.shutdown()
            thread.join()

    with ThreadingHTTPServer(("127.0.0.1", 0), FilterWithoutIdHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = ErambaClient(
                ErambaInstance(
                    name="real-values",
                    base_url=f"http://127.0.0.1:{server.server_port}",
                    token=BEARER_VALUE,
                )
            )
            CHECK.assertEqual(real_cli_first_item_id(client, "/laravel/api/assets/index"), "7")
            with pytest.raises(ValueError, match="No real id"):
                real_cli_first_filter_id(client)
        finally:
            server.shutdown()
            thread.join()


def test_real_cli_check_requires_instance_selection() -> None:
    with pytest.raises(SystemExit):
        real_cli_main(["--limit", "0"])


def test_real_cli_check_reports_target_setup_errors(tmp_path: Path) -> None:
    stream = io.StringIO()
    path = tmp_path / "instances.json"
    path.write_text(json.dumps({"instances": {"bad": []}}), encoding="utf-8")

    with contextlib.redirect_stdout(stream):
        code = real_cli_main(["--config", str(path), "--instance", "bad", "--limit", "0"])

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(report["results"], {"failure": 1})
    CHECK.assertEqual(report["total"], 0)
