# API v2 Commands

This reference is generated from `erambactl.commands.find_commands(group="api-v2")`.
It uses the checked-in static command catalog and does not use OpenAPI.

## Summary

- Commands: 209
- Methods: DELETE 1, GET 177, POST 11, PUT 20
- Commands with path parameters: 39
- Commands accepting a request body: 32
- Body command specs covered: 32
- Body commands with payload field flags: 28
- Body action commands without payload fields: 4

## Invocation

```bash
erambactl --config examples/instances.json --instance local-a api-v2 get-assets-index
erambactl --config examples/instances.json --instance local-a api-v2 put-assets-edit-id --id 1 --data-file payload.json
erambactl --config examples/instances.json --instance local-a api-v2 put-settings-authentication --connection-type ldap --auth-policies 1
erambactl --config examples/instances.json --all-instances api-v2 get-assets-index
```

Path parameters can be positional or passed with the endpoint-specific flags shown below.
Body-capable commands accept `--data`, `--data-file`, `--form`, and `--file` according to the normal CLI rules.
Commands with body field flags can build the JSON body directly from those flags; do not mix them with `--data`, `--data-file`, `--form`, or `--file`.
A `-` in Body Flags means the command is a body-capable API action with no known payload fields.

## Command Catalog

| Command | Resource | Method | Path | Path Flags | Body Flags |
|---|---|---|---|---|---|
| `erambactl api-v2 get-assets-section` | `assets` | `GET` | `/laravel/api/assets/section` | - | - |
| `erambactl api-v2 get-assets-index` | `assets` | `GET` | `/laravel/api/assets/index` | - | - |
| `erambactl api-v2 put-assets-edit-id` | `assets` | `PUT` | `/laravel/api/assets/edit/{id}` | `--id` | `--business-units`, `--name`, `--description`, `--grc-contacts`, `--asset-owners`, `--asset-guardians`, `--asset-users`, `--asset-labels`, `--asset-media-types`, `--related-assets`, `--legals`, `--review`, `--processes` |
| `erambactl api-v2 get-asset-reviews-section` | `asset-reviews` | `GET` | `/laravel/api/asset-reviews/section` | - | - |
| `erambactl api-v2 get-asset-reviews-index` | `asset-reviews` | `GET` | `/laravel/api/asset-reviews/index` | - | - |
| `erambactl api-v2 get-settings-authentication` | `settings` | `GET` | `/laravel/api/settings/authentication` | - | - |
| `erambactl api-v2 put-settings-authentication` | `settings` | `PUT` | `/laravel/api/settings/authentication` | - | `--connection-type`, `--ldap-connector-id`, `--oauth-connector-id`, `--saml-connector-id`, `--auth-policies`, `--auth-awareness`, `--auth-account-review`, `--auth-vendor-assessment` |
| `erambactl api-v2 get-authorizations-index` | `authorizations` | `GET` | `/laravel/api/authorizations/index` | - | - |
| `erambactl api-v2 put-authorizations-update` | `authorizations` | `PUT` | `/laravel/api/authorizations/update` | - | `--authorization`, `--group-id`, `--permission`, `--action` |
| `erambactl api-v2 put-authorizations-update-bulk` | `authorizations` | `PUT` | `/laravel/api/authorizations/update-bulk` | - | `--authorizations`, `--group-id`, `--permission` |
| `erambactl api-v2 get-business-continuities-section` | `business-continuities` | `GET` | `/laravel/api/business-continuities/section` | - | - |
| `erambactl api-v2 get-business-continuities-index` | `business-continuities` | `GET` | `/laravel/api/business-continuities/index` | - | - |
| `erambactl api-v2 get-business-continuity-plan-audits-section` | `business-continuity-plan-audits` | `GET` | `/laravel/api/business-continuity-plan-audits/section` | - | - |
| `erambactl api-v2 get-business-continuity-plan-audits-index` | `business-continuity-plan-audits` | `GET` | `/laravel/api/business-continuity-plan-audits/index` | - | - |
| `erambactl api-v2 get-business-continuity-plans-section` | `business-continuity-plans` | `GET` | `/laravel/api/business-continuity-plans/section` | - | - |
| `erambactl api-v2 get-business-continuity-plans-index` | `business-continuity-plans` | `GET` | `/laravel/api/business-continuity-plans/index` | - | - |
| `erambactl api-v2 get-business-continuity-reviews-section` | `business-continuity-reviews` | `GET` | `/laravel/api/business-continuity-reviews/section` | - | - |
| `erambactl api-v2 get-business-continuity-reviews-index` | `business-continuity-reviews` | `GET` | `/laravel/api/business-continuity-reviews/index` | - | - |
| `erambactl api-v2 get-business-continuity-tasks-section` | `business-continuity-tasks` | `GET` | `/laravel/api/business-continuity-tasks/section` | - | - |
| `erambactl api-v2 get-business-continuity-tasks-index` | `business-continuity-tasks` | `GET` | `/laravel/api/business-continuity-tasks/index` | - | - |
| `erambactl api-v2 get-business-continuities-threats-section` | `business-continuities` | `GET` | `/laravel/api/business-continuities/threats/section` | - | - |
| `erambactl api-v2 get-business-continuities-threats-index` | `business-continuities` | `GET` | `/laravel/api/business-continuities/threats/index` | - | - |
| `erambactl api-v2 get-business-continuities-vulnerabilities-section` | `business-continuities` | `GET` | `/laravel/api/business-continuities/vulnerabilities/section` | - | - |
| `erambactl api-v2 get-business-continuities-vulnerabilities-index` | `business-continuities` | `GET` | `/laravel/api/business-continuities/vulnerabilities/index` | - | - |
| `erambactl api-v2 get-business-units-section` | `business-units` | `GET` | `/laravel/api/business-units/section` | - | - |
| `erambactl api-v2 get-business-units-index` | `business-units` | `GET` | `/laravel/api/business-units/index` | - | - |
| `erambactl api-v2 get-compliance-analysis-findings-section` | `compliance-analysis-findings` | `GET` | `/laravel/api/compliance-analysis-findings/section` | - | - |
| `erambactl api-v2 get-compliance-analysis-findings-index` | `compliance-analysis-findings` | `GET` | `/laravel/api/compliance-analysis-findings/index` | - | - |
| `erambactl api-v2 get-compliance-exceptions-section` | `compliance-exceptions` | `GET` | `/laravel/api/compliance-exceptions/section` | - | - |
| `erambactl api-v2 get-compliance-exceptions-index` | `compliance-exceptions` | `GET` | `/laravel/api/compliance-exceptions/index` | - | - |
| `erambactl api-v2 get-compliance-managements-section` | `compliance-managements` | `GET` | `/laravel/api/compliance-managements/section` | - | - |
| `erambactl api-v2 get-compliance-managements-index` | `compliance-managements` | `GET` | `/laravel/api/compliance-managements/index` | - | - |
| `erambactl api-v2 get-compliance-package-items-section` | `compliance-package-items` | `GET` | `/laravel/api/compliance-package-items/section` | - | - |
| `erambactl api-v2 get-compliance-package-items-index` | `compliance-package-items` | `GET` | `/laravel/api/compliance-package-items/index` | - | - |
| `erambactl api-v2 get-compliance-package-regulators-section` | `compliance-package-regulators` | `GET` | `/laravel/api/compliance-package-regulators/section` | - | - |
| `erambactl api-v2 get-compliance-package-regulators-index` | `compliance-package-regulators` | `GET` | `/laravel/api/compliance-package-regulators/index` | - | - |
| `erambactl api-v2 get-data-assets-section` | `data-assets` | `GET` | `/laravel/api/data-assets/section` | - | - |
| `erambactl api-v2 get-data-assets-index` | `data-assets` | `GET` | `/laravel/api/data-assets/index` | - | - |
| `erambactl api-v2 get-data-asset-instances-section` | `data-asset-instances` | `GET` | `/laravel/api/data-asset-instances/section` | - | - |
| `erambactl api-v2 get-data-asset-instances-index` | `data-asset-instances` | `GET` | `/laravel/api/data-asset-instances/index` | - | - |
| `erambactl api-v2 get-goal-audits-section` | `goal-audits` | `GET` | `/laravel/api/goal-audits/section` | - | - |
| `erambactl api-v2 get-goal-audits-index` | `goal-audits` | `GET` | `/laravel/api/goal-audits/index` | - | - |
| `erambactl api-v2 get-goals-section` | `goals` | `GET` | `/laravel/api/goals/section` | - | - |
| `erambactl api-v2 get-goals-index` | `goals` | `GET` | `/laravel/api/goals/index` | - | - |
| `erambactl api-v2 put-goals-edit-id` | `goals` | `PUT` | `/laravel/api/goals/edit/{id}` | `--id` | `--name`, `--description`, `--owners`, `--contacts`, `--status`, `--audit-calendar-type`, `--audit-calendar-mode`, `--audit-periodical`, `--audit-specific`, `--audit-metric-description`, `--audit-success-criteria`, `--audit-owners`, `--audit-evidence-owners`, `--security-policies`, `--security-services`, `--risks`, `--third-party-risks`, `--business-continuities`, `--projects`, `--program-issues` |
| `erambactl api-v2 get-groups-section` | `groups` | `GET` | `/laravel/api/groups/section` | - | - |
| `erambactl api-v2 get-groups-index` | `groups` | `GET` | `/laravel/api/groups/index` | - | - |
| `erambactl api-v2 get-groups-list` | `groups` | `GET` | `/laravel/api/groups/list` | - | - |
| `erambactl api-v2 get-legals-section` | `legals` | `GET` | `/laravel/api/legals/section` | - | - |
| `erambactl api-v2 get-legals-index` | `legals` | `GET` | `/laravel/api/legals/index` | - | - |
| `erambactl api-v2 get-login-bans-section` | `login-bans` | `GET` | `/laravel/api/login-bans/section` | - | - |
| `erambactl api-v2 get-login-bans-index` | `login-bans` | `GET` | `/laravel/api/login-bans/index` | - | - |
| `erambactl api-v2 get-policy-exceptions-section` | `policy-exceptions` | `GET` | `/laravel/api/policy-exceptions/section` | - | - |
| `erambactl api-v2 get-policy-exceptions-index` | `policy-exceptions` | `GET` | `/laravel/api/policy-exceptions/index` | - | - |
| `erambactl api-v2 get-processes-section` | `processes` | `GET` | `/laravel/api/processes/section` | - | - |
| `erambactl api-v2 get-processes-index` | `processes` | `GET` | `/laravel/api/processes/index` | - | - |
| `erambactl api-v2 get-program-issues-section` | `program-issues` | `GET` | `/laravel/api/program-issues/section` | - | - |
| `erambactl api-v2 get-program-issues-index` | `program-issues` | `GET` | `/laravel/api/program-issues/index` | - | - |
| `erambactl api-v2 get-program-scopes-section` | `program-scopes` | `GET` | `/laravel/api/program-scopes/section` | - | - |
| `erambactl api-v2 get-program-scopes-index` | `program-scopes` | `GET` | `/laravel/api/program-scopes/index` | - | - |
| `erambactl api-v2 get-project-achievements-section` | `project-achievements` | `GET` | `/laravel/api/project-achievements/section` | - | - |
| `erambactl api-v2 get-project-achievements-index` | `project-achievements` | `GET` | `/laravel/api/project-achievements/index` | - | - |
| `erambactl api-v2 get-projects-section` | `projects` | `GET` | `/laravel/api/projects/section` | - | - |
| `erambactl api-v2 get-projects-index` | `projects` | `GET` | `/laravel/api/projects/index` | - | - |
| `erambactl api-v2 get-project-expenses-section` | `project-expenses` | `GET` | `/laravel/api/project-expenses/section` | - | - |
| `erambactl api-v2 get-project-expenses-index` | `project-expenses` | `GET` | `/laravel/api/project-expenses/index` | - | - |
| `erambactl api-v2 get-queue-section` | `queue` | `GET` | `/laravel/api/queue/section` | - | - |
| `erambactl api-v2 get-queue-index` | `queue` | `GET` | `/laravel/api/queue/index` | - | - |
| `erambactl api-v2 get-queued-jobs-section` | `queued-jobs` | `GET` | `/laravel/api/queued-jobs/section` | - | - |
| `erambactl api-v2 get-queued-jobs-index` | `queued-jobs` | `GET` | `/laravel/api/queued-jobs/index` | - | - |
| `erambactl api-v2 get-risks-section` | `risks` | `GET` | `/laravel/api/risks/section` | - | - |
| `erambactl api-v2 get-risks-index` | `risks` | `GET` | `/laravel/api/risks/index` | - | - |
| `erambactl api-v2 get-risk-exceptions-section` | `risk-exceptions` | `GET` | `/laravel/api/risk-exceptions/section` | - | - |
| `erambactl api-v2 get-risk-exceptions-index` | `risk-exceptions` | `GET` | `/laravel/api/risk-exceptions/index` | - | - |
| `erambactl api-v2 get-risk-reviews-section` | `risk-reviews` | `GET` | `/laravel/api/risk-reviews/section` | - | - |
| `erambactl api-v2 get-risk-reviews-index` | `risk-reviews` | `GET` | `/laravel/api/risk-reviews/index` | - | - |
| `erambactl api-v2 get-risks-threats-section` | `risks` | `GET` | `/laravel/api/risks/threats/section` | - | - |
| `erambactl api-v2 get-risks-threats-index` | `risks` | `GET` | `/laravel/api/risks/threats/index` | - | - |
| `erambactl api-v2 get-risks-vulnerabilities-section` | `risks` | `GET` | `/laravel/api/risks/vulnerabilities/section` | - | - |
| `erambactl api-v2 get-risks-vulnerabilities-index` | `risks` | `GET` | `/laravel/api/risks/vulnerabilities/index` | - | - |
| `erambactl api-v2 get-security-incidents-section` | `security-incidents` | `GET` | `/laravel/api/security-incidents/section` | - | - |
| `erambactl api-v2 get-security-incidents-index` | `security-incidents` | `GET` | `/laravel/api/security-incidents/index` | - | - |
| `erambactl api-v2 get-security-incident-stages-security-incidents-section` | `security-incident-stages-security-incidents` | `GET` | `/laravel/api/security-incident-stages-security-incidents/section` | - | - |
| `erambactl api-v2 get-security-incident-stages-security-incidents-index` | `security-incident-stages-security-incidents` | `GET` | `/laravel/api/security-incident-stages-security-incidents/index` | - | - |
| `erambactl api-v2 get-security-policies-section` | `security-policies` | `GET` | `/laravel/api/security-policies/section` | - | - |
| `erambactl api-v2 get-security-policies-index` | `security-policies` | `GET` | `/laravel/api/security-policies/index` | - | - |
| `erambactl api-v2 get-security-policy-reviews-section` | `security-policy-reviews` | `GET` | `/laravel/api/security-policy-reviews/section` | - | - |
| `erambactl api-v2 get-security-policy-reviews-index` | `security-policy-reviews` | `GET` | `/laravel/api/security-policy-reviews/index` | - | - |
| `erambactl api-v2 get-security-service-audits-section` | `security-service-audits` | `GET` | `/laravel/api/security-service-audits/section` | - | - |
| `erambactl api-v2 get-security-service-audits-index` | `security-service-audits` | `GET` | `/laravel/api/security-service-audits/index` | - | - |
| `erambactl api-v2 get-security-services-section` | `security-services` | `GET` | `/laravel/api/security-services/section` | - | - |
| `erambactl api-v2 get-security-services-index` | `security-services` | `GET` | `/laravel/api/security-services/index` | - | - |
| `erambactl api-v2 get-security-service-issues-section` | `security-service-issues` | `GET` | `/laravel/api/security-service-issues/section` | - | - |
| `erambactl api-v2 get-security-service-issues-index` | `security-service-issues` | `GET` | `/laravel/api/security-service-issues/index` | - | - |
| `erambactl api-v2 get-security-service-maintenances-section` | `security-service-maintenances` | `GET` | `/laravel/api/security-service-maintenances/section` | - | - |
| `erambactl api-v2 get-security-service-maintenances-index` | `security-service-maintenances` | `GET` | `/laravel/api/security-service-maintenances/index` | - | - |
| `erambactl api-v2 get-service-contracts-section` | `service-contracts` | `GET` | `/laravel/api/service-contracts/section` | - | - |
| `erambactl api-v2 get-service-contracts-index` | `service-contracts` | `GET` | `/laravel/api/service-contracts/index` | - | - |
| `erambactl api-v2 get-settings-brute-force-protection` | `settings` | `GET` | `/laravel/api/settings/brute-force-protection` | - | - |
| `erambactl api-v2 get-settings-currency` | `settings` | `GET` | `/laravel/api/settings/currency` | - | - |
| `erambactl api-v2 get-settings-email` | `settings` | `GET` | `/laravel/api/settings/email` | - | - |
| `erambactl api-v2 get-settings-debug` | `settings` | `GET` | `/laravel/api/settings/debug` | - | - |
| `erambactl api-v2 get-settings-help-improve` | `settings` | `GET` | `/laravel/api/settings/help-improve` | - | - |
| `erambactl api-v2 get-settings-timezone` | `settings` | `GET` | `/laravel/api/settings/timezone` | - | - |
| `erambactl api-v2 get-settings-backup` | `settings` | `GET` | `/laravel/api/settings/backup` | - | - |
| `erambactl api-v2 get-settings-risk-granularity` | `settings` | `GET` | `/laravel/api/settings/risk-granularity` | - | - |
| `erambactl api-v2 get-settings-pdf` | `settings` | `GET` | `/laravel/api/settings/pdf` | - | - |
| `erambactl api-v2 get-settings-ssl-offload` | `settings` | `GET` | `/laravel/api/settings/ssl-offload` | - | - |
| `erambactl api-v2 get-settings-csv` | `settings` | `GET` | `/laravel/api/settings/csv` | - | - |
| `erambactl api-v2 get-settings-crontab` | `settings` | `GET` | `/laravel/api/settings/crontab` | - | - |
| `erambactl api-v2 get-settings-default-translation` | `settings` | `GET` | `/laravel/api/settings/default-translation` | - | - |
| `erambactl api-v2 get-settings-webhooks` | `settings` | `GET` | `/laravel/api/settings/webhooks` | - | - |
| `erambactl api-v2 get-settings-activity-log` | `settings` | `GET` | `/laravel/api/settings/activity-log` | - | - |
| `erambactl api-v2 get-settings-default-dashboard` | `settings` | `GET` | `/laravel/api/settings/default-dashboard` | - | - |
| `erambactl api-v2 get-settings-custom-logo` | `settings` | `GET` | `/laravel/api/settings/custom-logo` | - | - |
| `erambactl api-v2 get-settings-custom-logo-file` | `settings` | `GET` | `/laravel/api/settings/custom-logo/file` | - | - |
| `erambactl api-v2 get-settings-version` | `settings` | `GET` | `/laravel/api/settings/version` | - | - |
| `erambactl api-v2 get-settings-legacy-ui` | `settings` | `GET` | `/laravel/api/settings/legacyUi` | - | - |
| `erambactl api-v2 get-settings-about` | `settings` | `GET` | `/laravel/api/settings/about` | - | - |
| `erambactl api-v2 get-settings-test-mail-connection` | `settings` | `PUT` | `/laravel/api/settings/test-mail-connection` | - | `--test-email`, `--smtp-use`, `--email-name`, `--no-reply-email`, `--queue-transport-limit` |
| `erambactl api-v2 get-settings-deactivate-license` | `settings` | `POST` | `/laravel/api/settings/deactivate-license` | - | `--client-key` |
| `erambactl api-v2 get-settings-crontab-info` | `settings` | `GET` | `/laravel/api/settings/crontab-info` | - | - |
| `erambactl api-v2 get-settings-activate-license` | `settings` | `POST` | `/laravel/api/settings/activate-license` | - | `--client-key` |
| `erambactl api-v2 get-settings-system-health` | `settings` | `GET` | `/laravel/api/settings/system-health` | - | - |
| `erambactl api-v2 get-settings-public-address` | `settings` | `GET` | `/laravel/api/settings/public-address` | - | - |
| `erambactl api-v2 get-settings-test-public-address` | `settings` | `PUT` | `/laravel/api/settings/test-public-address` | - | `--public-address` |
| `erambactl api-v2 get-settings-version-info` | `settings` | `GET` | `/laravel/api/settings/version-info` | - | - |
| `erambactl api-v2 post-settings-reset-database` | `settings` | `POST` | `/laravel/api/settings/reset-database` | - | `--reset-db` |
| `erambactl api-v2 post-settings-reset-application-id` | `settings` | `POST` | `/laravel/api/settings/reset-application-id` | - | `--reset-app-id` |
| `erambactl api-v2 post-settings-remove-legacy-views` | `settings` | `POST` | `/laravel/api/settings/remove-legacy-views` | - | `--remove-legacy-views` |
| `erambactl api-v2 post-settings-flush-emails-in-queue` | `settings` | `POST` | `/laravel/api/settings/flush-emails-in-queue` | - | - |
| `erambactl api-v2 get-team-roles-section` | `team-roles` | `GET` | `/laravel/api/team-roles/section` | - | - |
| `erambactl api-v2 get-team-roles-index` | `team-roles` | `GET` | `/laravel/api/team-roles/index` | - | - |
| `erambactl api-v2 get-third-parties-section` | `third-parties` | `GET` | `/laravel/api/third-parties/section` | - | - |
| `erambactl api-v2 get-third-parties-index` | `third-parties` | `GET` | `/laravel/api/third-parties/index` | - | - |
| `erambactl api-v2 get-third-party-risks-section` | `third-party-risks` | `GET` | `/laravel/api/third-party-risks/section` | - | - |
| `erambactl api-v2 get-third-party-risks-index` | `third-party-risks` | `GET` | `/laravel/api/third-party-risks/index` | - | - |
| `erambactl api-v2 get-third-party-risk-reviews-section` | `third-party-risk-reviews` | `GET` | `/laravel/api/third-party-risk-reviews/section` | - | - |
| `erambactl api-v2 get-third-party-risk-reviews-index` | `third-party-risk-reviews` | `GET` | `/laravel/api/third-party-risk-reviews/index` | - | - |
| `erambactl api-v2 get-third-party-risks-threats-section` | `third-party-risks` | `GET` | `/laravel/api/third-party-risks/threats/section` | - | - |
| `erambactl api-v2 get-third-party-risks-threats-index` | `third-party-risks` | `GET` | `/laravel/api/third-party-risks/threats/index` | - | - |
| `erambactl api-v2 get-third-party-risks-vulnerabilities-section` | `third-party-risks` | `GET` | `/laravel/api/third-party-risks/vulnerabilities/section` | - | - |
| `erambactl api-v2 get-third-party-risks-vulnerabilities-index` | `third-party-risks` | `GET` | `/laravel/api/third-party-risks/vulnerabilities/index` | - | - |
| `erambactl api-v2 get-user-system-logs-section` | `user-system-logs` | `GET` | `/laravel/api/user-system-logs/section` | - | - |
| `erambactl api-v2 get-user-system-logs-index` | `user-system-logs` | `GET` | `/laravel/api/user-system-logs/index` | - | - |
| `erambactl api-v2 get-visualisation-settings` | `visualisation-settings` | `GET` | `/laravel/api/visualisation-settings` | - | - |
| `erambactl api-v2 put-visualisation-settings-edit-status-id` | `visualisation-settings` | `PUT` | `/laravel/api/visualisation-settings/{id}/edit-status` | `--id` | `--status` |
| `erambactl api-v2 get-activity-log-activity-logs-section-model-alias` | `activity-log` | `GET` | `/laravel/api/activity-log/activity-logs/section/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-activity-log-activity-logs-index-model-alias` | `activity-log` | `GET` | `/laravel/api/activity-log/activity-logs/index/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-activity-log-activity-logs-share-model-alias-activity-log-id` | `activity-log` | `GET` | `/laravel/api/activity-log/activity-logs/share/{modelAlias}/{activityLogId}` | `--model-alias`, `--activity-log-id` | - |
| `erambactl api-v2 get-activity-log-activity-logs-archive-section-model-alias` | `activity-log` | `GET` | `/laravel/api/activity-log/activity-logs/archive/section/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-activity-log-activity-logs-archive-index-model-alias` | `activity-log` | `GET` | `/laravel/api/activity-log/activity-logs/archive/index/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-activity-log-activity-logs-archive-share-model-alias-activity-log-id` | `activity-log` | `GET` | `/laravel/api/activity-log/activity-logs/archive/share/{modelAlias}/{activityLogId}` | `--model-alias`, `--activity-log-id` | - |
| `erambactl api-v2 get-app-notifications-check` | `app-notifications` | `GET` | `/laravel/api/app-notifications/check` | - | - |
| `erambactl api-v2 get-app-notifications-list` | `app-notifications` | `GET` | `/laravel/api/app-notifications/list` | - | - |
| `erambactl api-v2 put-app-notifications-id-view` | `app-notifications` | `PUT` | `/laravel/api/app-notifications/{id}/view` | `--id` | - |
| `erambactl api-v2 get-cron-section` | `cron` | `GET` | `/laravel/api/cron/section` | - | - |
| `erambactl api-v2 get-cron-index` | `cron` | `GET` | `/laravel/api/cron/index` | - | - |
| `erambactl api-v2 get-dashboard-dashboard-reports-section` | `dashboard` | `GET` | `/laravel/api/dashboard/dashboard-reports/section` | - | - |
| `erambactl api-v2 get-dashboard-dashboard-reports-index` | `dashboard` | `GET` | `/laravel/api/dashboard/dashboard-reports/index` | - | - |
| `erambactl api-v2 get-custom-dynamic-status-custom-dynamic-statuses-section-model-alias` | `custom-dynamic-status` | `GET` | `/laravel/api/custom-dynamic-status/custom-dynamic-statuses/section/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-custom-dynamic-status-custom-dynamic-statuses-index-model-alias` | `custom-dynamic-status` | `GET` | `/laravel/api/custom-dynamic-status/custom-dynamic-statuses/index/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-custom-dynamic-status-custom-dynamic-statuses-edit-status-enabled-id` | `custom-dynamic-status` | `PUT` | `/laravel/api/custom-dynamic-status/custom-dynamic-statuses/edit-status-enabled/{id}` | `--id` | `--enabled` |
| `erambactl api-v2 put-custom-dynamic-status-custom-dynamic-statuses-edit-status-visible-id` | `custom-dynamic-status` | `PUT` | `/laravel/api/custom-dynamic-status/custom-dynamic-statuses/edit-status-visible/{id}` | `--id` | `--visible` |
| `erambactl api-v2 get-filters-model-alias-index` | `filters` | `GET` | `/laravel/api/filters/{modelAlias}/index` | `--model-alias` | - |
| `erambactl api-v2 get-filters-id` | `filters` | `GET` | `/laravel/api/filters/{id}` | `--id` | - |
| `erambactl api-v2 put-filters-id` | `filters` | `PUT` | `/laravel/api/filters/{id}` | `--id` | `--filter`, `--view`, `--update` |
| `erambactl api-v2 delete-filters-id` | `filters` | `DELETE` | `/laravel/api/filters/{id}` | `--id` | - |
| `erambactl api-v2 get-filters-id-timestamp` | `filters` | `GET` | `/laravel/api/filters/{id}/timestamp` | `--id` | - |
| `erambactl api-v2 get-filters` | `filters` | `GET` | `/laravel/api/filters` | - | - |
| `erambactl api-v2 post-filters` | `filters` | `POST` | `/laravel/api/filters` | - | `--name`, `--model`, `--params` |
| `erambactl api-v2 get-filters-id-share` | `filters` | `GET` | `/laravel/api/filters/{id}/share` | `--id` | - |
| `erambactl api-v2 put-filters-id-share` | `filters` | `PUT` | `/laravel/api/filters/{id}/share` | `--id` | `--view`, `--update`, `--options` |
| `erambactl api-v2 get-filters-id-destroy-get` | `filters` | `GET` | `/laravel/api/filters/{id}/destroy_get` | `--id` | - |
| `erambactl api-v2 get-filters-model-alias-field-options-field` | `filters` | `GET` | `/laravel/api/filters/{modelAlias}/field-options/{field}` | `--model-alias`, `--field` | - |
| `erambactl api-v2 put-filters-id-pin` | `filters` | `PUT` | `/laravel/api/filters/{id}/pin` | `--id` | `--pin` |
| `erambactl api-v2 put-filters-id-default` | `filters` | `PUT` | `/laravel/api/filters/{id}/default` | `--id` | `--default` |
| `erambactl api-v2 put-filters-id-params` | `filters` | `PUT` | `/laravel/api/filters/{id}/params` | `--id` | `--params` |
| `erambactl api-v2 put-filters-id-default-for-all` | `filters` | `PUT` | `/laravel/api/filters/{id}/default-for-all` | `--id` | `--default-for-all` |
| `erambactl api-v2 get-customization-customization-model-alias` | `customization` | `GET` | `/laravel/api/customization/customization/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 put-customization-customization-model-alias` | `customization` | `PUT` | `/laravel/api/customization/customization/{modelAlias}` | `--model-alias` | `--custom-fields` |
| `erambactl api-v2 post-customization-customization-reset-model-alias` | `customization` | `POST` | `/laravel/api/customization/customization/reset/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-ldap-ldap-connectors` | `ldap` | `GET` | `/laravel/api/ldap/ldap-connectors/index` | - | - |
| `erambactl api-v2 get-ldap-ldap-connectors-index` | `ldap` | `GET` | `/laravel/api/ldap/ldap-connectors/index` | - | - |
| `erambactl api-v2 get-ldap-ldap-synchronizations-section` | `ldap-sync` | `GET` | `/laravel/api/ldap-sync/ldap-synchronizations/section` | - | - |
| `erambactl api-v2 get-ldap-ldap-synchronizations-index` | `ldap-sync` | `GET` | `/laravel/api/ldap-sync/ldap-synchronizations/index` | - | - |
| `erambactl api-v2 get-ldap-sync-ldap-synchronization-system-logs-section` | `ldap-sync` | `GET` | `/laravel/api/ldap-sync/ldap-synchronization-system-logs/section` | - | - |
| `erambactl api-v2 get-ldap-sync-ldap-synchronization-system-logs-index` | `ldap-sync` | `GET` | `/laravel/api/ldap-sync/ldap-synchronization-system-logs/index` | - | - |
| `erambactl api-v2 get-notifications-notification-system-items-section-model-alias` | `notifications` | `GET` | `/laravel/api/notifications/notification-system-items/section/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-notifications-notification-system-items-index-model-alias` | `notifications` | `GET` | `/laravel/api/notifications/notification-system-items/index/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 put-notifications-notification-system-items-edit-status-id` | `notifications` | `PUT` | `/laravel/api/notifications/notification-system-items/edit-status/{id}` | `--id` | `--status` |
| `erambactl api-v2 get-oauth-oauth-connectors-section` | `oauth` | `GET` | `/laravel/api/oauth/oauth-connectors/section` | - | - |
| `erambactl api-v2 get-oauth-oauth-connectors-index` | `oauth` | `GET` | `/laravel/api/oauth/oauth-connectors/index` | - | - |
| `erambactl api-v2 get-purifier-purifier-tags-section` | `purifier` | `GET` | `/laravel/api/purifier/purifier-tags/section` | - | - |
| `erambactl api-v2 get-purifier-purifier-tags-index` | `purifier` | `GET` | `/laravel/api/purifier/purifier-tags/index` | - | - |
| `erambactl api-v2 get-saml-saml-connectors-section` | `saml` | `GET` | `/laravel/api/saml/saml-connectors/section` | - | - |
| `erambactl api-v2 get-saml-saml-connectors-index` | `saml` | `GET` | `/laravel/api/saml/saml-connectors/index` | - | - |
| `erambactl api-v2 get-translations-translations-section` | `translations` | `GET` | `/laravel/api/translations/translations/section` | - | - |
| `erambactl api-v2 get-translations-translations-index` | `translations` | `GET` | `/laravel/api/translations/translations/index` | - | - |
| `erambactl api-v2 get-translations-translations-edit-status-id` | `translations` | `PUT` | `/laravel/api/translations/translations/edit-status/{id}` | `--id` | `--status` |
| `erambactl api-v2 get-triggers-triggers-section-model-alias` | `triggers` | `GET` | `/laravel/api/triggers/triggers/section/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 get-triggers-triggers-index-model-alias` | `triggers` | `GET` | `/laravel/api/triggers/triggers/index/{modelAlias}` | `--model-alias` | - |
| `erambactl api-v2 post-triggers-triggers-test-trigger-model` | `triggers` | `POST` | `/laravel/api/triggers/triggers/test-trigger/{model}` | `--model` | `--global`, `--runtime`, `--name`, `--language`, `--timeout`, `--composer-packages`, `--code` |
| `erambactl api-v2 post-triggers-triggers-test-trigger-formatting-model` | `triggers` | `POST` | `/laravel/api/triggers/triggers/test-trigger-formatting/{model}` | `--model` | `--global`, `--runtime`, `--name`, `--language`, `--timeout`, `--composer-packages`, `--code` |
| `erambactl api-v2 post-triggers-triggers-test-trigger-validate-model` | `triggers` | `POST` | `/laravel/api/triggers/triggers/test-trigger-validate/{model}` | `--model` | `--global`, `--runtime`, `--name`, `--language`, `--timeout`, `--composer-packages`, `--code` |
| `erambactl api-v2 get-triggers-trigger-logs-section` | `triggers` | `GET` | `/laravel/api/triggers/trigger-logs/section` | - | - |
| `erambactl api-v2 get-triggers-trigger-logs-index` | `triggers` | `GET` | `/laravel/api/triggers/trigger-logs/index` | - | - |
| `erambactl api-v2 get-webhooks-webhook-requests-section` | `webhooks` | `GET` | `/laravel/api/webhooks/webhook-requests/section` | - | - |
| `erambactl api-v2 get-webhooks-webhook-requests-index` | `webhooks` | `GET` | `/laravel/api/webhooks/webhook-requests/index` | - | - |
