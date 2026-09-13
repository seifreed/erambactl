@echo off
setlocal

set "DB_NAME=docker"
set "DB_PASSWORD=Your_DB_user_P@ssw0rd"
set "DB_USER=docker"

for %%I in (a b) do (
  docker exec -i -e MYSQL_PWD="%DB_PASSWORD%" erambactl-%%I-mysql mysql -u "%DB_USER%" "%DB_NAME%" < "%~dp0eramba-fill-real-data.sql" || exit /b 1
  docker exec erambactl-%%I-eramba sh -lc "mkdir -p /var/www/eramba/app/upgrade/data/files/uploads && cp /var/www/eramba/app/upgrade/webroot/img/logo.png /var/www/eramba/app/upgrade/data/files/uploads/erambactl-real-logo.png && chown -R www-data:www-data /var/www/eramba/app/upgrade/logs /var/www/eramba/app/upgrade/data/files/uploads" || exit /b 1
  docker exec erambactl-%%I-eramba sh -lc "cd /var/www/eramba/app/upgrade && bin/cake access_control sync --quiet" || exit /b 1
)
