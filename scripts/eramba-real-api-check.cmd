@echo off
setlocal

set "ROOT_DIR=%~dp0.."
set "FAILURES=0"

call "%ROOT_DIR%\scripts\eramba-lab.cmd" bootstrap || exit /b 1
call "%ROOT_DIR%\scripts\eramba-fill-real-data.cmd" || exit /b 1
call "%ROOT_DIR%\scripts\eramba-seed-data.cmd" --all-instances || exit /b 1
call "%ROOT_DIR%\scripts\eramba-real-cli-check.cmd" ^
  --all-instances ^
  --group api-v2 ^
  --skip-method delete ^
  --skip-action get-settings-activate-license ^
  --skip-action get-filters-id-timestamp ^
  --skip-action post-settings-reset-application-id ^
  --skip-action post-settings-reset-database ^
  --request-timeout 5 ^
  --real-values ^
  --strict-http || set "FAILURES=1"
call "%ROOT_DIR%\scripts\eramba-real-cli-check.cmd" ^
  --all-instances ^
  --group api-v2 ^
  --action get-settings-activate-license ^
  --request-timeout 5 ^
  --real-values || set "FAILURES=1"
call "%ROOT_DIR%\scripts\eramba-real-cli-check.cmd" ^
  --all-instances ^
  --group api-v2 ^
  --action get-filters-id-timestamp ^
  --request-timeout 5 ^
  --real-values || set "FAILURES=1"
call "%ROOT_DIR%\scripts\eramba-real-cli-check.cmd" ^
  --all-instances ^
  --group api-v2 ^
  --method delete ^
  --request-timeout 5 ^
  --real-values ^
  --strict-http || set "FAILURES=1"
call "%ROOT_DIR%\scripts\eramba-real-cli-check.cmd" ^
  --all-instances ^
  --group api-v2 ^
  --action post-settings-reset-application-id ^
  --request-timeout 60 ^
  --real-values ^
  --strict-http || set "FAILURES=1"
call "%ROOT_DIR%\scripts\eramba-real-cli-check.cmd" ^
  --all-instances ^
  --group api-v2 ^
  --action post-settings-reset-database ^
  --request-timeout 60 ^
  --real-values ^
  --strict-http || set "FAILURES=1"
exit /b %FAILURES%
