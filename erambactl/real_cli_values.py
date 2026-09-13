from __future__ import annotations

from typing import Protocol, cast

from erambactl.api_v2_fields import V2_RAW_STRING_FIELDS
from erambactl.client import ErambaClient, ErambaError
from erambactl.commands import ApiCommand
from erambactl.types import ApiResult, JsonValue


class _TargetValues(Protocol):
    @property
    def values(self) -> dict[str, str]: ...


_ASSET_EMPTY_LIST_FIELDS = frozenset(
    {"AssetGuardians", "AssetUsers", "RelatedAssets", "Legals", "Processes"}
)
_GOAL_EMPTY_LIST_FIELDS = frozenset(
    {
        "AuditOwners",
        "AuditEvidenceOwners",
        "SecurityPolicies",
        "SecurityServices",
        "Risks",
        "ThirdPartyRisks",
        "BusinessContinuities",
        "Projects",
        "ProgramIssues",
    }
)
_FIELD_VALUES = {
    "connection_type": "default",
    "client_key": "x",
    "EMAIL_NAME": "erambactl",
    "PUBLIC_ADDRESS": "https://localhost",
    "QUEUE_TRANSPORT_LIMIT": "1",
    "model": "Assets",
    "authorizations": '["Assets"]',
    "authorization": "Assets",
    "action": "index",
    "group_id": "10",
    "elements": '{"general":{"hidden":"0","position":"0","elements":{}}}',
    "composer_packages": "",
    "language": "php",
    "timeout": "30",
    "code": "return true;",
}
_GOAL_FIELD_VALUES = {
    "Owners": '["User-1"]',
    "Contacts": '["User-1"]',
    "status": "current",
    "audit_calendar_type": "0",
}
_NULL_FIELDS = frozenset({"ldap_connector_id", "oauth_connector_id", "saml_connector_id"})
_ZERO_FIELDS = frozenset(
    {
        "auth_awareness",
        "auth_account_review",
        "auth_vendor_assessment",
        "SMTP_USE",
        "global",
        "runtime",
    }
)
_ONE_FIELDS = frozenset(
    {"auth_policies", "reset_db", "remove_legacy_views", "pinned", "default", "permission"}
)
_EMAIL_FIELDS = frozenset({"test_email", "NO_REPLY_EMAIL"})
_EMPTY_LIST_FIELDS = frozenset({"view", "update", "options"})
_EMPTY_OBJECT_FIELDS = frozenset({"customFields"})
_DATE_FIELDS = frozenset({"review", "audit_specific"})


def _path_value(command: ApiCommand, target: _TargetValues, parameter: str) -> str:
    value = _specific_path_value(command, target.values, parameter)
    if value is not None:
        return value
    if parameter.lower().endswith("id") or parameter.lower() == "id":
        return "0"
    if parameter == "modelAlias":
        if "notification-system-items" in command.action:
            return "Goals"
        return "Assets"
    if parameter == "field":
        if command.action == "get-filters-model-alias-field-options-field":
            return "asset_media_type_id"
        return "name"
    if parameter == "model":
        return "Assets"
    return "x"


def _specific_path_value(command: ApiCommand, values: dict[str, str], parameter: str) -> str | None:
    if parameter == "activityLogId":
        key = "archived_activity_log_id" if "archive" in command.action else "activity_log_id"
        return values.get(key)
    if parameter == "id":
        if command.resource == "assets":
            return values.get("asset_id")
        if command.resource == "goals":
            return values.get("goal_id")
        if command.resource == "filters":
            return values.get("filter_id")
        if command.resource == "app-notifications":
            return values.get("app_notification_id")
        if command.resource == "visualisation-settings":
            return values.get("visualisation_setting_id")
        if "custom-dynamic-status" in command.action:
            return values.get("dynamic_status_id")
        if "notification-system-items" in command.action:
            return values.get("notification_system_item_id")
        if command.resource == "translations":
            return values.get("translation_id")
    return None


def _field_value(command: ApiCommand, field: str) -> str:
    if field in V2_RAW_STRING_FIELDS.get(command.action, ()):
        return "{}"
    if command.action == "put-assets-edit-id":
        value = _asset_field_value(field)
        if value is not None:
            return value
    if command.action == "put-goals-edit-id":
        value = _goal_field_value(field)
        if value is not None:
            return value
    return _common_field_value(field)


def _common_field_value(field: str) -> str:
    if field in _FIELD_VALUES:
        return _FIELD_VALUES[field]
    if field in _NULL_FIELDS:
        return "null"
    if field in _ZERO_FIELDS:
        return "0"
    if field in _ONE_FIELDS:
        return "1"
    if field in _EMAIL_FIELDS:
        return "admin@eramba.org"
    if field.endswith("_id") or field == "id":
        return "1"
    if field.startswith(("is_", "allow_", "enable_")) or field in {"status", "visible", "enabled"}:
        return "1"
    if field in _EMPTY_LIST_FIELDS:
        return "[]"
    if field in _EMPTY_OBJECT_FIELDS:
        return "{}"
    if field in _DATE_FIELDS:
        return "2027-12-31"
    return "x"


def _asset_field_value(field: str) -> str | None:
    if field == "BusinessUnits":
        return "[1]"
    if field in {"AssetOwners", "GrcContacts"}:
        return '["User-1"]'
    if field == "AssetMediaTypes":
        return "1"
    if field in _ASSET_EMPTY_LIST_FIELDS:
        return "[]"
    if field == "AssetLabels":
        return "null"
    return None


def _goal_field_value(field: str) -> str | None:
    if field in _GOAL_EMPTY_LIST_FIELDS:
        return "[]"
    return _GOAL_FIELD_VALUES.get(field)


def _real_values(client: ErambaClient) -> dict[str, str]:
    return {
        "asset_id": _first_item_id(client, "/laravel/api/assets/index"),
        "goal_id": _first_item_id(client, "/laravel/api/goals/index"),
        "filter_id": _first_filter_id(client),
        "app_notification_id": _first_nested_id(client, "/laravel/api/app-notifications/list"),
        "visualisation_setting_id": _first_nested_id(client, "/laravel/api/visualisation-settings"),
        "activity_log_id": _first_item_id(
            client, "/laravel/api/activity-log/activity-logs/index/Assets"
        ),
        "archived_activity_log_id": _first_item_id(
            client, "/laravel/api/activity-log/activity-logs/archive/index/Assets"
        ),
        "dynamic_status_id": _first_item_id(
            client, "/laravel/api/custom-dynamic-status/custom-dynamic-statuses/index/Assets"
        ),
        "notification_system_item_id": _notification_system_item_id(client),
        "translation_id": _first_item_id(client, "/laravel/api/translations/translations/index"),
    }


def _notification_system_item_id(client: ErambaClient) -> str:
    try:
        return _first_item_id(
            client, "/laravel/api/notifications/notification-system-items/index/Goals"
        )
    except ErambaError:
        return "1"
    except ValueError:
        return "1"


def _first_filter_id(client: ErambaClient) -> str:
    result = client.request("GET", "/laravel/api/filters/Assets/index")
    filters = cast(dict[str, object], cast(dict[str, object], result)["data"])["filters"]
    for item in cast(list[dict[str, object]], filters):
        if item.get("user_id") == 1 and item.get("model") == "Assets":
            item_id = _id_value(item.get("id"))
            if item_id is None:
                raise ValueError("No real id found")
            return item_id
    return _first_nested_id_value(result)


def _first_item_id(client: ErambaClient, path: str) -> str:
    result = client.request("GET", path)
    items = cast(
        list[dict[str, object]],
        cast(
            dict[str, object],
            cast(dict[str, object], cast(dict[str, object], result)["data"])["data"],
        )["items"],
    )
    if not items:
        raise ValueError(f"No real data for {path}")
    item_id = _id_value(items[0].get("_id", items[0].get("id")))
    if item_id is None:
        raise ValueError(f"No real id found for {path}")
    return item_id


def _first_nested_id(client: ErambaClient, path: str) -> str:
    return _first_nested_id_value(client.request("GET", path))


def _first_nested_id_value(value: ApiResult) -> str:
    found = _find_id(value)
    if found is None:
        raise ValueError("No real id found")
    return found


def _find_id(value: JsonValue | bytes) -> str | None:
    if isinstance(value, dict):
        for key in ("_id", "id"):
            found = _id_value(value.get(key))
            if found is not None:
                return found
        for item in value.values():
            found = _find_id(item)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = _find_id(item)
            if found is not None:
                return found
    return None


def _id_value(value: object) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value:
        return value
    return None
