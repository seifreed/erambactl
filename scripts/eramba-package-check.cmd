@echo off
setlocal

set "ROOT_DIR=%~dp0.."
set "WORK_DIR=%TEMP%\erambactl-package-%RANDOM%%RANDOM%"
set "DIST_DIR=%WORK_DIR%\dist"
set "VENV_DIR=%WORK_DIR%\venv"
if "%PYTHON%"=="" set "PYTHON=py -3.14"

mkdir "%DIST_DIR%" || exit /b 1
%PYTHON% -m pip wheel --no-deps --no-build-isolation --wheel-dir "%DIST_DIR%" "%ROOT_DIR%" || goto fail
%PYTHON% -m venv "%VENV_DIR%" || goto fail
"%VENV_DIR%\Scripts\python.exe" -m pip install "%DIST_DIR%\erambactl-0.1.0-py3-none-any.whl" || goto fail
"%VENV_DIR%\Scripts\python.exe" -c "from erambactl import ErambaFleet, ErambaInstance, find_commands, get_command; command = get_command('get-assets-index', group='api-v2'); assert len(find_commands(group='api-v2')) == 209; assert command.path == '/laravel/api/assets/index'; assert ErambaFleet((ErambaInstance(name='local-a', base_url='https://localhost', token='x'),)).names() == ('local-a',); assert ErambaFleet(()).request_all('GET', '/x') == {}; assert ErambaFleet(()).run_all(command) == {}" || goto fail
"%VENV_DIR%\Scripts\erambactl.exe" commands --group api-v2 >nul || goto fail
"%VENV_DIR%\Scripts\erambactl-seed.exe" --help >nul || goto fail
"%VENV_DIR%\Scripts\erambactl-smoke.exe" --help >nul || goto fail
"%VENV_DIR%\Scripts\erambactl-real-cli-check.exe" --help >nul || goto fail
"%VENV_DIR%\Scripts\erambactl-route-data.exe" --help >nul || goto fail
echo package check passed
rmdir /s /q "%WORK_DIR%"
exit /b 0

:fail
rmdir /s /q "%WORK_DIR%"
exit /b 1
