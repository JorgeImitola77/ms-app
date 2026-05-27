@echo off
REM Escenario A: 50 usuarios concurrentes haciendo Crear durante 1 minuto.
REM Requiere:
REM   - Stack levantado: docker compose up -d
REM   - Variable LOADTEST_TOKEN exportada (ver loadtest\README.md)

set RUN_TIME=%RUN_TIME%
if "%RUN_TIME%"=="" set RUN_TIME=1m

set USERS=%USERS%
if "%USERS%"=="" set USERS=50

set SPAWN_RATE=%SPAWN_RATE%
if "%SPAWN_RATE%"=="" set SPAWN_RATE=10

if not exist loadtest\reports mkdir loadtest\reports

locust -f loadtest\locustfile.py --headless ^
    -u %USERS% -r %SPAWN_RATE% --run-time %RUN_TIME% ^
    --tags crear ^
    --host http://localhost ^
    --csv loadtest\reports\crear ^
    --html loadtest\reports\crear.html
