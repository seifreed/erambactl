from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from erambactl.api_v2_data import V2_ROUTES
from erambactl.route_data import ROUTES


@dataclass(frozen=True, slots=True)
class ApiCommand:
    group: str
    action: str
    resource: str
    method: str
    path: str
    path_params: tuple[str, ...] = ()
    accepts_body: bool = False


def format_command_path(command: ApiCommand, values: dict[str, str]) -> str:
    missing = [parameter for parameter in command.path_params if parameter not in values]
    if missing:
        raise ValueError(f"Missing path parameter: {missing[0]}")
    return command.path.format(
        **{parameter: quote(values[parameter], safe="") for parameter in command.path_params}
    )


def find_commands(
    *,
    group: str | None = None,
    resource: str | None = None,
    action: str | None = None,
    method: str | None = None,
    accepts_body: bool | None = None,
) -> tuple[ApiCommand, ...]:
    return tuple(
        command
        for command in API_COMMANDS
        if (group is None or command.group == group)
        and (resource is None or command.resource == resource)
        and (action is None or command.action == action)
        and (method is None or command.method == method.upper())
        and (accepts_body is None or command.accepts_body is accepts_body)
    )


def get_command(
    action: str, *, group: str | None = "api", resource: str | None = None
) -> ApiCommand:
    commands = find_commands(group=group, action=action, resource=resource)
    if len(commands) == 1:
        return commands[0]
    raise ValueError(f"Command not found: {action}")


API_COMMANDS: tuple[ApiCommand, ...] = tuple(
    ApiCommand("api", action, resource, method, path, params, accepts_body)
    for action, resource, method, path, params, accepts_body in ROUTES
) + tuple(
    ApiCommand("api-v2", action, resource, method, path, params, accepts_body)
    for action, resource, method, path, params, accepts_body in V2_ROUTES
)
API_GROUPS: tuple[str, ...] = tuple(sorted({command.group for command in API_COMMANDS}))
API_RESOURCES: tuple[str, ...] = tuple(sorted({command.resource for command in API_COMMANDS}))
