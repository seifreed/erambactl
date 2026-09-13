SET @now = NOW();
SET @asset_name = 'erambactl real asset';
SET @goal_name = 'erambactl real goal';
SET @business_unit_name = 'erambactl real business unit';

INSERT INTO business_units (
  name, description, created, modified
)
SELECT @business_unit_name, 'Created by erambactl real API tests', @now, @now
WHERE NOT EXISTS (SELECT 1 FROM business_units WHERE name = @business_unit_name AND deleted = 0);

INSERT INTO assets (
  name, description, review, security_incident_open_count, created, modified
)
SELECT @asset_name, 'Created by erambactl real API tests', DATE_ADD(CURDATE(), INTERVAL 1 YEAR), 0, @now, @now
WHERE NOT EXISTS (SELECT 1 FROM assets WHERE name = @asset_name AND deleted = 0);
SET @asset_id = (SELECT id FROM assets WHERE name = @asset_name AND deleted = 0 ORDER BY id DESC LIMIT 1);

INSERT INTO goals (
  name, owner_id, description, audit_metric_description, audit_success_criteria, status, created, modified
)
SELECT @goal_name, 1, 'Created by erambactl real API tests', 'Metric', 'Criteria', 'current', @now, @now
WHERE NOT EXISTS (SELECT 1 FROM goals WHERE name = @goal_name AND deleted = 0);

INSERT INTO app_notifications (
  notification, title, data, model, foreign_key, user_id, reference, seen, created, modified
)
SELECT 'erambactl.real', 'erambactl real notification', '{}', 'Assets', @asset_id, 1, 'erambactl-real-cli', 0, @now, @now
WHERE NOT EXISTS (SELECT 1 FROM app_notifications WHERE reference = 'erambactl-real-cli');

INSERT INTO notification_system_items (
  slug, status, name, description, model, filename, allow_notification, allow_webhook,
  allow_trigger, feedback, feedback_message, automated, email_customized, email_subject,
  email_body, email_type, type, status_feedback, feedback_show_item,
  feedback_completed_notification, log_count, created, modified
)
SELECT 'erambactl-real-cli', 1, 'erambactl real notification item',
  'Created by erambactl real API tests', 'Assets', 'erambactl_real',
  1, 0, 0, 0, '', 1, 1, 'erambactl real subject', 'erambactl real body',
  0, 'warning', 0, 0, 0, 0, @now, @now
WHERE NOT EXISTS (SELECT 1 FROM notification_system_items WHERE slug = 'erambactl-real-cli');

INSERT INTO activity_logs (
  user_id, user_name, model, foreign_key, type, field, field_label, old_value, new_value, created
)
SELECT 1, 'Admin Admin', 'Assets', @asset_id, 1, 'name', 'Name', '', @asset_name, @now
WHERE NOT EXISTS (SELECT 1 FROM activity_logs WHERE model = 'Assets' AND foreign_key = @asset_id);

INSERT INTO archived_activity_logs (
  user_id, user_name, model, foreign_key, type, field, field_label, old_value, new_value, created
)
SELECT 1, 'Admin Admin', 'Assets', @asset_id, 1, 'name', 'Name', '', @asset_name, @now
WHERE NOT EXISTS (SELECT 1 FROM archived_activity_logs WHERE model = 'Assets' AND foreign_key = @asset_id);

UPDATE settings
SET value = 'erambactl-real-logo.png', modified = @now
WHERE variable = 'CUSTOM_LOGO';

SELECT
  (SELECT id FROM assets WHERE name = @asset_name AND deleted = 0 ORDER BY id DESC LIMIT 1) AS asset_id,
  (SELECT id FROM business_units WHERE name = @business_unit_name AND deleted = 0 ORDER BY id DESC LIMIT 1) AS business_unit_id,
  (SELECT id FROM goals WHERE name = @goal_name AND deleted = 0 ORDER BY id DESC LIMIT 1) AS goal_id,
  (SELECT id FROM app_notifications WHERE reference = 'erambactl-real-cli' ORDER BY id DESC LIMIT 1) AS app_notification_id,
  (SELECT id FROM notification_system_items WHERE slug = 'erambactl-real-cli' ORDER BY id DESC LIMIT 1) AS notification_system_item_id,
  (SELECT id FROM activity_logs WHERE model = 'Assets' AND foreign_key = @asset_id ORDER BY id DESC LIMIT 1) AS activity_log_id,
  (SELECT id FROM archived_activity_logs WHERE model = 'Assets' AND foreign_key = @asset_id ORDER BY id DESC LIMIT 1) AS archived_activity_log_id;
