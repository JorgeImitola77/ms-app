@echo off
REM Escenario B: 100 usuarios concurrentes haciendo Consulta durante 1 minuto.
REM Antes de lanzar, escalar el servicio consulta a 3 réplicas:
REM     docker compose up -d --scale consulta=3
REM Requiere LOADTEST_TOKEN exportada (ver loadtest\README.md).

set RUN_TIME=%RUN_TIME%
if "%RUN_TIME%"=="" set RUN_TIME=1m

set USERS=%USERS%
if "%USERS%"=="" set USERS=100

set SPAWN_RATE=%SPAWN_RATE%
if "%SPAWN_RATE%"=="" set SPAWN_RATE=20

if not exist loadtest\reports mkdir loadtest\reports

locust -f loadtest\locustfile.py --headless ^
    -u %USERS% -r %SPAWN_RATE% --run-time %RUN_TIME% ^
    --tags consulta ^
    --host http://localhost ^
    --csv loadtest\reports\consulta ^
    --html loadtest\reports\consulta.html
