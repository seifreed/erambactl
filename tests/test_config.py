from __future__ import annotations

from tests.helpers import (
    BASIC_ENV_NAME,
    BEARER_VALUE,
    CHECK,
    COOKIE_VALUE,
    ENV_NAME,
    MISSING_ENV_NAME,
    Path,
    _instance,
    _parser,
    json,
    load_fleet,
    load_instance,
    os,
    pytest,
    tempfile,
)


def test_direct_instance_arguments() -> None:
    args = _parser().parse_args(
        ["--base-url", "https://one.example", "--token", BEARER_VALUE, "--insecure"]
    )

    instance = _instance(args)

    CHECK.assertEqual(instance.base_url, "https://one.example")
    CHECK.assertEqual(instance.token, BEARER_VALUE)
    CHECK.assertFalse(instance.verify_tls)
    CHECK.assertEqual(instance.timeout, 30.0)


def test_direct_instance_arguments_accept_timeout() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://one.example",
            "--token",
            BEARER_VALUE,
            "--timeout",
            "2.5",
        ]
    )

    instance = _instance(args)

    CHECK.assertEqual(instance.timeout, 2.5)


def test_direct_instance_arguments_accept_basic_auth() -> None:
    args = _parser().parse_args(
        [
            "--base-url",
            "https://one.example",
            "--username",
            "user",
            "--password",
            BEARER_VALUE,
            "--auth-mode",
            "basic",
        ]
    )

    instance = _instance(args)

    CHECK.assertEqual(instance.username, "user")
    CHECK.assertEqual(instance.password, BEARER_VALUE)
    CHECK.assertEqual(instance.auth_mode, "basic")


def test_direct_instance_arguments_accept_cookie() -> None:
    args = _parser().parse_args(["--base-url", "https://one.example", "--cookie", COOKIE_VALUE])

    instance = _instance(args)

    CHECK.assertEqual(instance.cookie, COOKIE_VALUE)


def test_loads_named_instance_from_config_basic_auth_env() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {
                            "base_url": "https://localhost:8443",
                            "username": "user",
                            "password_env": BASIC_ENV_NAME,
                            "auth_mode": "basic",
                        }
                    }
                }
            )
        )
        os.environ[BASIC_ENV_NAME] = BEARER_VALUE
        try:
            instance = load_instance(path, "local-a")
        finally:
            os.environ.pop(BASIC_ENV_NAME, None)

    CHECK.assertEqual(instance.username, "user")
    CHECK.assertEqual(instance.password, BEARER_VALUE)
    CHECK.assertEqual(instance.auth_mode, "basic")


def test_loads_named_instance_from_config_cookie_env() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {
                            "base_url": "https://localhost:8443",
                            "cookie_env": ENV_NAME,
                        }
                    }
                }
            )
        )
        os.environ[ENV_NAME] = COOKIE_VALUE
        try:
            instance = load_instance(path, "local-a")
        finally:
            os.environ.pop(ENV_NAME, None)

    CHECK.assertEqual(instance.cookie, COOKIE_VALUE)


def test_loads_named_instance_from_config_env_token() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {
                            "base_url": "https://localhost:8443",
                            "token_env": ENV_NAME,
                            "verify_tls": False,
                            "timeout": 4,
                        }
                    }
                }
            )
        )
        os.environ[ENV_NAME] = BEARER_VALUE
        try:
            instance = load_instance(path, "local-a")
        finally:
            os.environ.pop(ENV_NAME, None)

    CHECK.assertEqual(instance.base_url, "https://localhost:8443")
    CHECK.assertEqual(instance.token, BEARER_VALUE)
    CHECK.assertFalse(instance.verify_tls)
    CHECK.assertEqual(instance.timeout, 4.0)


def test_loads_fleet_from_config() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-b": {"base_url": "https://localhost:9443", "token": BEARER_VALUE},
                        "local-a": {"base_url": "https://localhost:8443", "token": BEARER_VALUE},
                    }
                }
            )
        )

        fleet = load_fleet(path)

    CHECK.assertEqual(fleet.client("local-a").instance.base_url, "https://localhost:8443")
    CHECK.assertEqual(fleet.client("local-b").instance.base_url, "https://localhost:9443")


def test_load_instance_errors_are_clear() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(json.dumps({"instances": {"bad": {"token": BEARER_VALUE}}}))

        with pytest.raises(ValueError, match="Instance not found"):
            load_instance(path, "missing")
        with pytest.raises(ValueError, match="base_url"):
            load_instance(path, "bad")


def test_load_fleet_rejects_invalid_instances_config() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(json.dumps({"instances": []}))

        with pytest.raises(TypeError, match="Invalid instances config"):
            load_fleet(path)


def test_load_fleet_rejects_non_object_config() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(json.dumps([]))

        with pytest.raises(TypeError, match="Invalid instances config"):
            load_fleet(path)


def test_load_instance_rejects_missing_env_token() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {"instances": {"local-a": {"base_url": "https://x", "token_env": MISSING_ENV_NAME}}}
            )
        )

        with pytest.raises(ValueError, match="Environment variable"):
            load_instance(path, "local-a")


def test_load_instance_rejects_invalid_timeout_type() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {
                            "base_url": "https://x",
                            "token": BEARER_VALUE,
                            "timeout": "soon",
                        }
                    }
                }
            )
        )

        with pytest.raises(TypeError, match="timeout"):
            load_instance(path, "local-a")


def test_load_instance_rejects_boolean_timeout() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {
                            "base_url": "https://x",
                            "token": BEARER_VALUE,
                            "timeout": True,
                        }
                    }
                }
            )
        )

        with pytest.raises(TypeError, match="timeout"):
            load_instance(path, "local-a")


def test_load_instance_rejects_invalid_verify_tls_type() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(
            json.dumps(
                {
                    "instances": {
                        "local-a": {
                            "base_url": "https://x",
                            "token": BEARER_VALUE,
                            "verify_tls": "false",
                        }
                    }
                }
            )
        )

        with pytest.raises(TypeError, match="verify_tls"):
            load_instance(path, "local-a")


def test_config_rejects_non_mapping_instance() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instances.json"
        path.write_text(json.dumps({"instances": {"bad": []}}))

        with pytest.raises(TypeError, match="Invalid instance config"):
            load_instance(path, "bad")
