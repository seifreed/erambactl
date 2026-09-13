from __future__ import annotations

from tests.helpers import (
    CHECK,
    Path,
    _route_source_from_catalog,
    cast,
    contextlib,
    get_command,
    io,
    parse_routes,
    pytest,
    render_route_data,
    route_data_difference,
    route_parser_main,
)


def test_route_parser_preserves_named_unnamed_and_duplicate_routes() -> None:
    source = """Route::middleware([
Route::get('/csrf-token', function (Request $request): void {
Route::get('/filters', [FilterController::class, 'store_get'])->name('filters.store_get');
Route::post('/app-messages/{messageId}/read', [AppMessageController::class, 'markRead']);
Route::get('/groups/list', [ GroupController::class, 'list' ])->name('Groups.list');
Route::get('/groups/list', [ GroupController::class, 'list' ])->name('Groups.list');
Route::get('portal/policy', [PolicyController::class, 'index'])->name('SecurityPolicyPortal.index');"""

    routes = parse_routes(source)

    CHECK.assertEqual(
        routes,
        (
            ("get-csrf-token", "csrf-token", "GET", "/laravel/api/csrf-token", (), False),
            ("get-filters-store-get", "filters", "GET", "/laravel/api/filters", (), False),
            (
                "post-app-messages-message-id-read",
                "app-messages",
                "POST",
                "/laravel/api/app-messages/{messageId}/read",
                ("messageId",),
                True,
            ),
            ("get-groups-list", "groups", "GET", "/laravel/api/groups/list", (), False),
            ("get-groups-list-2", "groups", "GET", "/laravel/api/groups/list", (), False),
            (
                "get-security-policy-portal-index",
                "portal",
                "GET",
                "/laravel/api/portal/policy",
                (),
                False,
            ),
        ),
    )


def test_route_parser_reports_differences_and_renders_route_data() -> None:
    source = "Route::post('/only-one/{itemId}', [OnlyController::class, 'store'])->name('OnlyOne.create');"
    routes = parse_routes(source)

    CHECK.assertEqual(
        route_data_difference(source), "route count mismatch: catalog has 1383, parsed 1"
    )
    CHECK.assertEqual(
        render_route_data(routes),
        "from __future__ import annotations\n"
        "\n"
        "ROUTES: tuple[tuple[str, str, str, str, tuple[str, ...], bool], ...] = (\n"
        "    (\n"
        '        "post-only-one-create",\n'
        '        "only-one",\n'
        '        "POST",\n'
        '        "/laravel/api/only-one/{itemId}",\n'
        '        ("itemId",),\n'
        "        True,\n"
        "    ),\n"
        ")\n",
    )


def test_route_parser_escapes_generated_string_literals() -> None:
    rendered = render_route_data(
        (
            (
                'get-route-"quoted"',
                'route-"quoted"',
                "GET",
                '/laravel/api/route/"quoted"/slash\\path',
                ('item"Id',),
                False,
            ),
        )
    )

    compile(rendered, "<route_data>", "exec")
    CHECK.assertIn(r'"get-route-\"quoted\""', rendered)
    CHECK.assertIn(r'"/laravel/api/route/\"quoted\"/slash\\path"', rendered)


def test_route_parser_verifies_full_catalog_source(tmp_path: Path) -> None:
    route_file = tmp_path / "api.php"
    route_file.write_text(_route_source_from_catalog(), encoding="utf-8")
    output = io.StringIO()

    CHECK.assertIsNone(route_data_difference(route_file.read_text(encoding="utf-8")))
    with contextlib.redirect_stdout(output):
        exit_code = route_parser_main([str(route_file)])

    CHECK.assertEqual(exit_code, 0)
    CHECK.assertEqual(output.getvalue(), "route catalog matches 1383 routes\n")


def test_route_parser_reports_same_length_route_mismatch() -> None:
    source = _route_source_from_catalog().replace("'/csrf-token'", "'/not-csrf'", 1)

    difference = route_data_difference(source)

    CHECK.assertIsNotNone(difference)
    CHECK.assertIn("route mismatch at 1", cast(str, difference))


def test_route_parser_main_verifies_and_prints(tmp_path: Path) -> None:
    route_file = tmp_path / "api.php"
    route_file.write_text(
        "Route::get('/only-one', [OnlyController::class, 'index']);", encoding="utf-8"
    )
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        exit_code = route_parser_main([str(route_file), "--print"])

    CHECK.assertEqual(exit_code, 0)
    CHECK.assertIn("get-only-one", output.getvalue())

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = route_parser_main([str(route_file)])

    CHECK.assertEqual(exit_code, 1)
    CHECK.assertEqual(output.getvalue(), "route count mismatch: catalog has 1383, parsed 1\n")


def test_get_command_errors_are_clear() -> None:
    with pytest.raises(ValueError, match="not found"):
        get_command("missing-command")
