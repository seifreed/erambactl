@echo off
setlocal

set "ROOT_DIR=%~dp0.."
if "%ERAMBA_PATH_ID%"=="" set "ERAMBA_PATH_ID=0"
if "%PYTHON%"=="" set "PYTHON=py -3.14"

%PYTHON% -c "from erambactl.smoke import main; raise SystemExit(main())" ^
  --config "%ROOT_DIR%\examples\instances.json" ^
  --all-instances ^
  --all ^
  --group api-v2 ^
  --dry-run ^
  --path-value "id=%ERAMBA_PATH_ID%" ^
  --summary-only ^
  %*
