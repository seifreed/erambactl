@echo off
setlocal

set "ROOT_DIR=%~dp0.."
set "UPSTREAM_DIR=%ROOT_DIR%\.eramba-docker-src"
set "BASE_FILE=%UPSTREAM_DIR%\docker-compose.simple-install.yml"
set "DB_NAME=docker"
set "DB_PASSWORD=Your_DB_user_P@ssw0rd"
set "DB_USER=docker"
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=ps"
if not "%~1"=="" shift

if not exist "%UPSTREAM_DIR%\.git" (
  git clone --depth 1 https://github.com/eramba/docker.git "%UPSTREAM_DIR%" || exit /b 1
)

if "%COMMAND%"=="up" (
  docker compose --project-directory "%UPSTREAM_DIR%" --project-name "erambactl-a" --env-file "%ROOT_DIR%\docker\eramba-a.env" -f "%BASE_FILE%" -f "%ROOT_DIR%\docker\eramba-a.yml" up -d %* || exit /b 1
  docker compose --project-directory "%UPSTREAM_DIR%" --project-name "erambactl-b" --env-file "%ROOT_DIR%\docker\eramba-b.env" -f "%BASE_FILE%" -f "%ROOT_DIR%\docker\eramba-b.yml" up -d %* || exit /b 1
  exit /b 0
)

if "%COMMAND%"=="down" (
  docker compose --project-directory "%UPSTREAM_DIR%" --project-name "erambactl-b" --env-file "%ROOT_DIR%\docker\eramba-b.env" -f "%BASE_FILE%" -f "%ROOT_DIR%\docker\eramba-b.yml" down %* || exit /b 1
  docker compose --project-directory "%UPSTREAM_DIR%" --project-name "erambactl-a" --env-file "%ROOT_DIR%\docker\eramba-a.env" -f "%BASE_FILE%" -f "%ROOT_DIR%\docker\eramba-a.yml" down %* || exit /b 1
  exit /b 0
)

if "%COMMAND%"=="bootstrap" (
  docker exec -e MYSQL_PWD="%DB_PASSWORD%" erambactl-a-mysql mysql -u "%DB_USER%" "%DB_NAME%" -e "UPDATE users SET api_allow = 1 WHERE login = 'admin'; SELECT id, login, api_allow FROM users WHERE login = 'admin';" || exit /b 1
  docker exec -e MYSQL_PWD="%DB_PASSWORD%" erambactl-b-mysql mysql -u "%DB_USER%" "%DB_NAME%" -e "UPDATE users SET api_allow = 1 WHERE login = 'admin'; SELECT id, login, api_allow FROM users WHERE login = 'admin';" || exit /b 1
  exit /b 0
)

docker compose --project-directory "%UPSTREAM_DIR%" --project-name "erambactl-a" --env-file "%ROOT_DIR%\docker\eramba-a.env" -f "%BASE_FILE%" -f "%ROOT_DIR%\docker\eramba-a.yml" %COMMAND% %* || exit /b 1
docker compose --project-directory "%UPSTREAM_DIR%" --project-name "erambactl-b" --env-file "%ROOT_DIR%\docker\eramba-b.env" -f "%BASE_FILE%" -f "%ROOT_DIR%\docker\eramba-b.yml" %COMMAND% %* || exit /b 1
exit /b 0
