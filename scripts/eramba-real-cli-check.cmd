@echo off
setlocal

set "ROOT_DIR=%~dp0.."
if "%PYTHON%"=="" set "PYTHON=py -3.14"

%PYTHON% -c "from erambactl.real_cli_check import main; raise SystemExit(main())" ^
  --config "%ROOT_DIR%\examples\instances.json" ^
  %*
