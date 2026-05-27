@echo off
REM Escenario C: 20 usuarios concurrentes haciendo consultas RAG durante 1 minuto.
REM Requiere n8n levantado y workflow rag-consulta importado.

set RUN_TIME=%RUN_TIME%
if "%RUN_TIME%"=="" set RUN_TIME=1m

set USERS=%USERS%
if "%USERS%"=="" set USERS=20

set SPAWN_RATE=%SPAWN_RATE%
if "%SPAWN_RATE%"=="" set SPAWN_RATE=5

if not exist loadtest\reports mkdir loadtest\reports

locust -f loadtest\locustfile.py --headless ^
    -u %USERS% -r %SPAWN_RATE% --run-time %RUN_TIME% ^
    --tags rag ^
    --host http://localhost ^
    --csv loadtest\reports\rag ^
    --html loadtest\reports\rag.html
