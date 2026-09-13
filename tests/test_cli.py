from __future__ import annotations

from tests.helpers import (
    API_COMMANDS,
    API_GROUPS,
    API_RESOURCES,
    BEARER_VALUE,
    CHECK,
    SESSION_COOKIE_VALUE,
    V2_BODY_FIELDS,
    V2_ROUTES,
    ApiCommand,
    JsonHandler,
    Path,
    ThreadingHTTPServer,
    UploadFile,
    _body,
    _catalog,
    _config,
    _file,
    _parser,
    _payload,
    _print_catalog,
    _print_result,
    _query,
    argparse,
    contextlib,
    erambactl,
    find_commands,
    format_command_path,
    get_command,
    io,
    json,
    main,
    pytest,
    runpy,
    sys,
    tempfile,
    threading,
)


def test_public_library_exports_upload_file() -> None:
    CHECK.assertIs(erambactl.UploadFile, UploadFile)
    CHECK.assertIs(erambactl.ApiCommand, ApiCommand)
    CHECK.assertIs(erambactl.API_COMMANDS, API_COMMANDS)
    CHECK.assertIs(erambactl.API_GROUPS, API_GROUPS)
    CHECK.assertIs(erambactl.API_RESOURCES, API_RESOURCES)
    CHECK.assertIs(erambactl.V2_ROUTES, V2_ROUTES)
    CHECK.assertIs(erambactl.V2_BODY_FIELDS, V2_BODY_FIELDS)
    CHECK.assertIs(erambactl.find_commands, find_commands)
    CHECK.assertIs(erambactl.format_command_path, format_command_path)
    CHECK.assertIs(erambactl.get_command, get_command)
    CHECK.assertIn("ApiCommand", erambactl.__all__)
    CHECK.assertIn("API_COMMANDS", erambactl.__all__)
    CHECK.assertIn("API_GROUPS", erambactl.__all__)
    CHECK.assertIn("API_RESOURCES", erambactl.__all__)
    CHECK.assertIn("V2_ROUTES", erambactl.__all__)
    CHECK.assertIn("V2_BODY_FIELDS", erambactl.__all__)
    CHECK.assertIn("find_commands", erambactl.__all__)
    CHECK.assertIn("format_command_path", erambactl.__all__)
    CHECK.assertIn("get_command", erambactl.__all__)
    CHECK.assertIn("UploadFile", erambactl.__all__)
    CHECK.assertIn("ApiResult", erambactl.__all__)
    CHECK.assertIn("Query", erambactl.__all__)


def test_package_module_delegates_to_cli() -> None:
    stream = io.StringIO()
    original_argv = sys.argv
    sys.argv = ["erambactl", "commands", "--group", "api-v2"]
    try:
        with contextlib.redirect_stdout(stream), pytest.raises(SystemExit) as caught:
            runpy.run_module("erambactl", run_name="__main__")
    finally:
        sys.argv = original_argv

    CHECK.assertEqual(caught.value.code, 0)
    CHECK.assertEqual(len(json.loads(stream.getvalue())), 209)


def test_parser_registers_explicit_api_commands() -> None:
    namespace = argparse.Namespace()
    CHECK.assertIs(_parser().parse_args(["commands"], namespace=namespace), namespace)

    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api",
            "get-assets-view",
            "assets",
            "7",
        ]
    )

    CHECK.assertEqual(args.command.method, "GET")
    CHECK.assertEqual(args.command.path, "/laravel/api/assets/view/{id}")
    CHECK.assertEqual(args.id, "7")


def test_parser_registers_direct_api_commands_without_resource_repetition() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api",
            "get-assets-view",
            "7",
        ]
    )

    CHECK.assertEqual(args.command.path, "/laravel/api/assets/view/{id}")
    CHECK.assertEqual(args.resource, "assets")
    CHECK.assertEqual(args.id, "7")


def test_parser_registers_named_path_parameter_flags() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api-v2",
            "put-assets-edit-id",
            "--id",
            "7",
            "--data",
            "{}",
        ]
    )

    CHECK.assertEqual(args.command.path, "/laravel/api/assets/edit/{id}")
    CHECK.assertEqual(args.resource, "assets")
    CHECK.assertEqual(args.id, "7")


def test_parser_registers_explicit_api_v2_commands() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api-v2",
            "put-assets-edit-id",
            "assets",
            "7",
            "--data",
            "{}",
        ]
    )

    CHECK.assertEqual(args.command.method, "PUT")
    CHECK.assertEqual(args.command.path, "/laravel/api/assets/edit/{id}")
    CHECK.assertEqual(args.id, "7")


def test_parser_rejects_wrong_direct_path_parameter_count() -> None:
    with pytest.raises(SystemExit):
        _parser().parse_args(
            [
                "--base-url",
                "https://localhost:8443",
                "--token",
                BEARER_VALUE,
                "api",
                "get-assets-view",
            ]
        )


def test_parser_help_shows_direct_command_path_arguments() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream), pytest.raises(SystemExit):
        _parser().parse_args(["api", "get-assets-view", "--help"])

    CHECK.assertIn("erambactl api get-assets-view [assets] id", stream.getvalue())
    CHECK.assertIn("path parameters: id", stream.getvalue())


def test_parser_help_shows_legacy_resource_for_index_commands() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream), pytest.raises(SystemExit):
        _parser().parse_args(["api-v2", "get-assets-index", "--help"])

    CHECK.assertIn("erambactl api-v2 get-assets-index [assets]", stream.getvalue())
    CHECK.assertIn("optional legacy resource prefix: assets", stream.getvalue())


def test_parser_help_shows_api_v2_endpoint_field_flags() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream), pytest.raises(SystemExit):
        _parser().parse_args(["api-v2", "put-customization-customization-model-alias", "--help"])

    CHECK.assertIn("--model-alias", stream.getvalue())
    CHECK.assertIn("--elements", stream.getvalue())


def test_parser_help_preserves_api_v2_acronym_field_flags() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream), pytest.raises(SystemExit):
        _parser().parse_args(["api-v2", "get-settings-test-mail-connection", "--help"])

    CHECK.assertIn("--smtp-use", stream.getvalue())
    CHECK.assertIn("--no-reply-email", stream.getvalue())
    CHECK.assertIn("--queue-transport-limit", stream.getvalue())


def test_api_registers_commands_for_each_static_resource() -> None:
    CHECK.assertEqual(API_GROUPS, ("api", "api-v2"))
    CHECK.assertEqual(len(V2_ROUTES), 209)
    CHECK.assertEqual(len(API_RESOURCES), 94)
    CHECK.assertEqual(len(API_COMMANDS), 1592)


def test_api_v2_body_field_specs_cover_every_body_command() -> None:
    body_commands = find_commands(group="api-v2", accepts_body=True)

    CHECK.assertEqual(set(V2_BODY_FIELDS), {command.action for command in body_commands})
    CHECK.assertEqual(len(V2_BODY_FIELDS), 32)


def test_parser_registers_every_static_api_command() -> None:
    parser = _parser()

    for command in API_COMMANDS:
        legacy_args = parser.parse_args(
            [
                "--base-url",
                "https://localhost:8443",
                "--token",
                BEARER_VALUE,
                command.group,
                command.action,
                command.resource,
                *(f"value-{parameter}" for parameter in command.path_params),
            ]
        )
        direct_args = parser.parse_args(
            [
                "--base-url",
                "https://localhost:8443",
                "--token",
                BEARER_VALUE,
                command.group,
                command.action,
                *(f"value-{parameter}" for parameter in command.path_params),
            ]
        )

        CHECK.assertIs(legacy_args.command, command)
        CHECK.assertEqual(legacy_args.resource, command.resource)
        CHECK.assertIs(direct_args.command, command)
        CHECK.assertEqual(direct_args.resource, command.resource)


def test_parser_registers_nested_api_commands() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api",
            "post-attachments-store",
            "attachments",
            "10",
            "22",
        ]
    )

    CHECK.assertEqual(args.command.path, "/laravel/api/attachments/{modelAlias}/{foreignKey}")
    CHECK.assertEqual(args.modelAlias, "10")
    CHECK.assertEqual(args.foreignKey, "22")


def test_parser_registers_mixed_positional_and_named_path_parameters() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api",
            "post-attachments-store",
            "Assets",
            "--foreign-key",
            "22",
        ]
    )

    CHECK.assertEqual(args.command.path, "/laravel/api/attachments/{modelAlias}/{foreignKey}")
    CHECK.assertEqual(args.modelAlias, "Assets")
    CHECK.assertEqual(args.foreignKey, "22")


def test_parser_rejects_duplicate_positional_and_named_path_parameters() -> None:
    with pytest.raises(SystemExit):
        _parser().parse_args(
            [
                "--base-url",
                "https://localhost:8443",
                "--token",
                BEARER_VALUE,
                "api-v2",
                "put-assets-edit-id",
                "7",
                "--id",
                "8",
                "--data",
                "{}",
            ]
        )


def test_parser_registers_repeated_actions_for_separate_resources() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://localhost:8443",
            "--token",
            BEARER_VALUE,
            "api",
            "get-business-units-index",
            "business-units",
        ]
    )

    CHECK.assertEqual(args.command.path, "/laravel/api/business-units/index")


def test_parser_rejects_crud_actions_missing_from_static_controller() -> None:
    parser = _parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["api", "create", "users", "--data", "{}"])


def test_main_prints_help_without_command() -> None:
    CHECK.assertEqual(main([]), 2)


def test_main_returns_error_for_missing_instance() -> None:
    CHECK.assertEqual(main(["api", "get-assets-index", "assets"]), 1)


def test_main_runs_a_real_local_request() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            code = main(
                [
                    "--base-url",
                    f"http://127.0.0.1:{server.server_port}",
                    "--token",
                    BEARER_VALUE,
                    "api",
                    "get-assets-index",
                    "assets",
                    "--query",
                    "page=2",
                    "--header",
                    "X-Trace=cli",
                ]
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)


def test_main_sends_dry_run_header() -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api",
                        "get-assets-index",
                        "assets",
                        "--query",
                        "page=2",
                        "--header",
                        "X-Trace=cli",
                        "--dry-run",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(json.loads(stream.getvalue())["dry_run"], "1")


def test_main_prints_session_cookie() -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--username",
                        "user",
                        "--password",
                        BEARER_VALUE,
                        "login",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(stream.getvalue().strip(), f"{SESSION_COOKIE_VALUE}; translation=1")


def test_print_result_writes_bytes() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream):
        _print_result(b"raw")

    CHECK.assertEqual(stream.getvalue(), "raw")


def test_print_result_writes_bytes_to_stdout_buffer(
    capfd: pytest.CaptureFixture[str],
) -> None:
    _print_result(b"raw")

    output, _error = capfd.readouterr()

    CHECK.assertEqual(output, "raw")


def test_main_prints_explicit_command_catalog() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream):
        code = main(["commands", "--resource", "assets", "--action", "post-assets-create-post"])

    rows = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(len(rows), 1)
    CHECK.assertEqual(rows[0]["action"], "post-assets-create-post")
    CHECK.assertEqual(rows[0]["path_params"], [])
    CHECK.assertTrue(rows[0]["accepts_body"])


def test_main_prints_text_command_catalog() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stdout(stream):
        code = main(
            [
                "commands",
                "--group",
                "api-v2",
                "--resource",
                "assets",
                "--action",
                "put-assets-edit-id",
                "--format",
                "text",
            ]
        )

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(
        stream.getvalue(),
        "api-v2 put-assets-edit-id id\tPUT\t/laravel/api/assets/edit/{id}\n",
    )


def test_main_runs_api_command_across_all_configured_instances(tmp_path: Path) -> None:
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
                code = main(
                    [
                        "--config",
                        str(config),
                        "--all-instances",
                        "api",
                        "get-assets-index",
                        "assets",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(
        json.loads(stream.getvalue()),
        {"local-a": {"method": "GET"}, "local-b": {"method": "GET"}},
    )


def test_main_summarizes_binary_results_across_all_configured_instances(tmp_path: Path) -> None:
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
                code = main(
                    [
                        "--config",
                        str(config),
                        "--all-instances",
                        "api",
                        "get-attachments-download",
                        "attachments",
                        "1",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(
        json.loads(stream.getvalue()), {"local-a": {"bytes": 8}, "local-b": {"bytes": 8}}
    )


def test_main_reports_all_instance_errors_without_hiding_success(tmp_path: Path) -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            config = _config(tmp_path, f"http://127.0.0.1:{server.server_port}", "file:///tmp/x")
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--config",
                        str(config),
                        "--all-instances",
                        "api",
                        "get-assets-index",
                        "assets",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(report["local-a"], {"method": "GET"})
    CHECK.assertIn("Unsupported URL scheme", report["local-b"]["error"])


def test_main_requires_config_for_all_instances() -> None:
    stream = io.StringIO()

    with contextlib.redirect_stderr(stream):
        code = main(["--all-instances", "api", "get-assets-index", "assets"])

    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(stream.getvalue(), "Use --config with --all-instances\n")


def test_main_logs_into_all_configured_instances(tmp_path: Path) -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            config = tmp_path / "instances.json"
            config.write_text(
                json.dumps(
                    {
                        "instances": {
                            "local-a": {
                                "base_url": f"http://127.0.0.1:{server.server_port}",
                                "username": "user",
                                "password": BEARER_VALUE,
                            },
                            "local-b": {
                                "base_url": f"http://127.0.0.1:{server.server_port}",
                                "username": "user",
                                "password": BEARER_VALUE,
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(stream):
                code = main(["--config", str(config), "--all-instances", "login"])
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(
        json.loads(stream.getvalue()),
        {
            "local-a": f"{SESSION_COOKIE_VALUE}; translation=1",
            "local-b": f"{SESSION_COOKIE_VALUE}; translation=1",
        },
    )


def test_main_posts_json_body_from_file() -> None:
    with tempfile.TemporaryDirectory() as directory:
        data_path = Path(directory) / "payload.json"
        data_path.write_text('{"name": "CRM"}', encoding="utf-8")
        with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api",
                        "post-assets-create-post",
                        "assets",
                        "--data-file",
                        str(data_path),
                    ]
                )
            finally:
                server.shutdown()
                thread.join()

    CHECK.assertEqual(code, 0)


def test_main_posts_multipart_payload() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "note.txt"
        path.write_text("hello", encoding="utf-8")
        with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api",
                        "post-attachments-store-form-create",
                        "attachments",
                        "Assets",
                        "file",
                        "--form",
                        "name=Evidence",
                        "--file",
                        f"file={path}",
                    ]
                )
            finally:
                server.shutdown()
                thread.join()

    CHECK.assertEqual(code, 0)


def test_main_sends_api_v2_endpoint_field_payload() -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api-v2",
                        "put-settings-authentication",
                        "--connection-type",
                        "ldap",
                        "--auth-policies",
                        "1",
                        "--ldap-connector-id",
                        "null",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(
        json.loads(stream.getvalue())["body"],
        {"auth_policies": 1, "connection_type": "ldap", "ldap_connector_id": None},
    )


def test_main_wraps_api_v2_edit_field_payload_in_data() -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api-v2",
                        "put-assets-edit-id",
                        "--id",
                        "7",
                        "--name",
                        "CRM",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(json.loads(stream.getvalue())["body"], {"data": {"name": "CRM"}})


def test_api_v2_data_wrapped_command_without_payload_sends_no_body() -> None:
    command = get_command("put-assets-edit-id", group="api-v2")
    args = _parser().parse_args(
        [
            "--base-url",
            "https://one.example",
            "--token",
            BEARER_VALUE,
            "api-v2",
            command.action,
            "7",
        ]
    )

    CHECK.assertEqual(_payload(args, command), (None, None, ()))


def test_main_sends_api_v2_raw_json_string_endpoint_field_payload() -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api-v2",
                        "post-filters",
                        "--name",
                        "Mine",
                        "--model",
                        "Assets",
                        "--params",
                        '{"select":{"name":{"display":"default"}}}',
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(
        json.loads(stream.getvalue())["body"],
        {
            "model": "Assets",
            "name": "Mine",
            "params": '{"select":{"name":{"display":"default"}}}',
        },
    )


def test_main_sends_api_v2_object_endpoint_field_payload() -> None:
    stream = io.StringIO()
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with contextlib.redirect_stdout(stream):
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api-v2",
                        "put-customization-customization-model-alias",
                        "--model-alias",
                        "Assets",
                        "--elements",
                        "[]",
                    ]
                )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(json.loads(stream.getvalue())["body"], {"elements": []})


def test_main_rejects_mixed_endpoint_fields_and_json_payload() -> None:
    with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            code = main(
                [
                    "--base-url",
                    f"http://127.0.0.1:{server.server_port}",
                    "--token",
                    BEARER_VALUE,
                    "api-v2",
                    "put-settings-authentication",
                    "--connection-type",
                    "ldap",
                    "--data",
                    "{}",
                ]
            )
        finally:
            server.shutdown()
            thread.join()

    CHECK.assertEqual(code, 1)


def test_main_rejects_mixed_json_and_multipart_payloads() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "note.txt"
        path.write_text("hello", encoding="utf-8")
        with ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--token",
                        BEARER_VALUE,
                        "api",
                        "post-attachments-store-form-create",
                        "attachments",
                        "Assets",
                        "file",
                        "--data",
                        "{}",
                        "--file",
                        f"file={path}",
                    ]
                )
            finally:
                server.shutdown()
                thread.join()

    CHECK.assertEqual(code, 1)


def test_query_parses_repeated_key_value_options() -> None:
    CHECK.assertEqual(
        _query(["ids[]=1", "ids[]=2", "filter=active"]),
        (("ids[]", "1"), ("ids[]", "2"), ("filter", "active")),
    )


def test_query_rejects_values_without_equals() -> None:
    with pytest.raises(ValueError, match="Invalid query parameter"):
        _query(["page"])


def test_file_parses_field_path_options() -> None:
    upload = _file("file=note.txt")

    CHECK.assertEqual(upload.field, "file")
    CHECK.assertEqual(upload.path, Path("note.txt"))


def test_file_rejects_values_without_equals() -> None:
    with pytest.raises(ValueError, match="Invalid file field"):
        _file("note.txt")


def test_body_accepts_json_objects_only() -> None:
    CHECK.assertEqual(_body('{"name": "CRM"}'), {"name": "CRM"})
    with pytest.raises(TypeError, match="JSON object"):
        _body("[]")


def test_body_reads_json_object_from_file() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "payload.json"
        path.write_text('{"name": "CRM"}', encoding="utf-8")

        body = _body(None, path)

    CHECK.assertEqual(body, {"name": "CRM"})


def test_body_requires_inline_data_or_file() -> None:
    with pytest.raises(ValueError, match="Use --data or --data-file"):
        _body(None)


def test_catalog_contains_every_explicit_command() -> None:
    catalog = _catalog()

    CHECK.assertEqual(len(catalog), len(API_COMMANDS))
    CHECK.assertIn("users", {row["resource"] for row in catalog})


def test_catalog_filters_explicit_commands() -> None:
    catalog = _catalog("assets", "get-assets-index", group="api")

    CHECK.assertEqual(
        catalog,
        [
            {
                "action": "get-assets-index",
                "accepts_body": False,
                "group": "api",
                "method": "GET",
                "path": "/laravel/api/assets/index",
                "path_params": [],
                "body_fields": [],
                "resource": "assets",
            }
        ],
    )


def test_catalog_filters_by_method_and_body_support() -> None:
    catalog = _catalog(resource="assets", method="post", accepts_body="yes")

    CHECK.assertIn("post-assets-create-post", {row["action"] for row in catalog})
    CHECK.assertNotIn("get-assets-index", {row["action"] for row in catalog})


def test_catalog_filters_by_group() -> None:
    catalog = _catalog(group="api-v2", resource="assets", method="put")

    CHECK.assertEqual(
        catalog,
        [
            {
                "action": "put-assets-edit-id",
                "accepts_body": True,
                "group": "api-v2",
                "method": "PUT",
                "path": "/laravel/api/assets/edit/{id}",
                "path_params": ["id"],
                "body_fields": [
                    "BusinessUnits",
                    "name",
                    "description",
                    "GrcContacts",
                    "AssetOwners",
                    "AssetGuardians",
                    "AssetUsers",
                    "AssetLabels",
                    "AssetMediaTypes",
                    "RelatedAssets",
                    "Legals",
                    "review",
                    "Processes",
                ],
                "resource": "assets",
            }
        ],
    )


def test_print_catalog_defaults_to_json() -> None:
    stream = io.StringIO()
    catalog: list[dict[str, object]] = [
        {"action": "get-assets-index", "group": "api", "path_params": []}
    ]

    with contextlib.redirect_stdout(stream):
        _print_catalog(catalog, "json")

    CHECK.assertEqual(json.loads(stream.getvalue()), catalog)


def test_api_v2_uses_live_methods_for_documented_aliases() -> None:
    methods = {
        action: get_command(action, group="api-v2").method
        for action in (
            "get-settings-test-mail-connection",
            "get-settings-deactivate-license",
            "get-settings-activate-license",
            "get-settings-test-public-address",
            "get-custom-dynamic-status-custom-dynamic-statuses-edit-status-enabled-id",
            "get-translations-translations-edit-status-id",
        )
    }

    CHECK.assertEqual(
        methods,
        {
            "get-settings-test-mail-connection": "PUT",
            "get-settings-deactivate-license": "POST",
            "get-settings-activate-license": "POST",
            "get-settings-test-public-address": "PUT",
            "get-custom-dynamic-status-custom-dynamic-statuses-edit-status-enabled-id": "PUT",
            "get-translations-translations-edit-status-id": "PUT",
        },
    )


def test_public_command_lookup_helpers() -> None:
    commands = find_commands(group="api", resource="assets", method="post", accepts_body=True)
    command = get_command("get-assets-view")

    CHECK.assertEqual(get_command("get-assets-index").action, "get-assets-index")
    CHECK.assertEqual(
        get_command("get-assets-index", group="api-v2").path,
        "/laravel/api/assets/index",
    )
    CHECK.assertEqual(get_command("post-assets-create-post", resource="assets").resource, "assets")
    CHECK.assertIn("post-assets-create-post", {command.action for command in commands})
    CHECK.assertEqual(
        format_command_path(command, {"id": "space/slash ?"}),
        "/laravel/api/assets/view/space%2Fslash%20%3F",
    )
