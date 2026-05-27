@echo off
setlocal EnableDelayedExpansion
set "ROOT=%~dp0"
set "VENV_PY=%ROOT%.venv-test\Scripts\python.exe"
set "VENV_LOCUST=%ROOT%.venv-test\Scripts\locust.exe"
set "TESTS=%ROOT%microservicios"
set "LOAD=%ROOT%loadtest"

if not exist "%VENV_PY%" (
    echo No existe %VENV_PY%
    echo Crea el venv primero:
    echo     py -3.13 -m venv .venv-test
    echo     .venv-test\Scripts\python.exe -m pip install fastapi==0.115.12 pydantic==2.11.1 "pydantic[email]" httpx==0.28.1 pytest==9.0.3 pytest-asyncio pytest-cov python-jose passlib bcrypt python-multipart asyncpg sqlalchemy
    echo     .venv-test\Scripts\python.exe -m pip install -r loadtest\requirements.txt
    if "%~1"=="" pause
    exit /b 1
)

if not "%~1"=="" (
    "%VENV_PY%" -m pytest "%TESTS%" %*
    exit /b %errorlevel%
)

:menu
cls
echo.
echo ========================================
echo    ms-app  ^|  Suite de tests
echo ========================================
echo   Unit / integration
echo   [1] Todos los tests
echo   [2] Todos los tests + coverage
echo   [3] Un microservicio
echo   [4] Solo modelos Pydantic ^(RF9^)
echo   [5] Filtrar por nombre ^(-k^)
echo.
echo   Carga ^(locust, requiere stack arriba^)
echo   [6] Crear     50 usuarios x 1m
echo   [7] Consulta  100 usuarios x 1m ^(--scale consulta=3^)
echo   [8] RAG       20 usuarios x 1m
echo   [9] Las 3 cargas secuenciales
echo.
echo   [0] Salir
echo ========================================
choice /c 0123456789 /n /m "Elegir [0-9]: "
set "OPT=!errorlevel!"

if "!OPT!"=="1" goto end
if "!OPT!"=="2" goto run_all
if "!OPT!"=="3" goto run_cov
if "!OPT!"=="4" goto menu_service
if "!OPT!"=="5" goto run_models
if "!OPT!"=="6" goto run_filter
if "!OPT!"=="7" goto load_crear
if "!OPT!"=="8" goto load_consulta
if "!OPT!"=="9" goto load_rag
if "!OPT!"=="10" goto load_all
goto end

:run_all
"%VENV_PY%" -m pytest "%TESTS%"
goto after_run

:run_cov
"%VENV_PY%" -m pytest "%TESTS%" --cov --cov-report=term-missing
goto after_run

:run_models
"%VENV_PY%" -m pytest "%TESTS%\tests\test_models.py" -v
goto after_run

:run_filter
echo.
set "PATTERN="
set /p "PATTERN=Patron (-k): "
if "!PATTERN!"=="" goto menu
"%VENV_PY%" -m pytest "%TESTS%" -k "!PATTERN!" -v
goto after_run

:menu_service
cls
echo.
echo ----------------------------------------
echo   Elegir microservicio
echo ----------------------------------------
echo   [1] ms-crear
echo   [2] ms-modificar
echo   [3] ms-consultar
echo   [4] ms-borrar
echo   [5] ms-log
echo   [0] Volver
echo ----------------------------------------
choice /c 012345 /n /m "Elegir [0-5]: "
set "SVC=!errorlevel!"

set "FILE="
if "!SVC!"=="2" set "FILE=test_ms_crear.py"
if "!SVC!"=="3" set "FILE=test_ms_modificar.py"
if "!SVC!"=="4" set "FILE=test_ms_consultar.py"
if "!SVC!"=="5" set "FILE=test_ms_borrar.py"
if "!SVC!"=="6" set "FILE=test_ms_log.py"
if "!FILE!"=="" goto menu

"%VENV_PY%" -m pytest "%TESTS%\tests\!FILE!" -v
goto after_run

:load_check
if not exist "%VENV_LOCUST%" (
    echo.
    echo [carga] locust no esta instalado en .venv-test.
    echo Instalalo con:
    echo     .venv-test\Scripts\python.exe -m pip install -r loadtest\requirements.txt
    goto after_run
)
if not exist "%LOAD%\reports" mkdir "%LOAD%\reports"
if "%LOADTEST_TOKEN%"=="" (
    echo.
    echo [carga] ADVERTENCIA: LOADTEST_TOKEN no esta definido.
    echo Los endpoints autenticados devolveran 401.
    echo Genera un token con:
    echo     set LOADTEST_TOKEN=^<tu_jwt^>
    echo o usa loadtest\get_token.py (ver loadtest\README.md).
    echo.
)
exit /b 0

:load_crear
call :load_check
if errorlevel 1 goto after_run
"%VENV_LOCUST%" -f "%LOAD%\locustfile.py" --headless -u 50 -r 10 --run-time 1m --csv "%LOAD%\reports\crear" --html "%LOAD%\reports\crear.html" CrearUser
goto after_run

:load_consulta
call :load_check
if errorlevel 1 goto after_run
"%VENV_LOCUST%" -f "%LOAD%\locustfile.py" --headless -u 100 -r 20 --run-time 1m --csv "%LOAD%\reports\consulta" --html "%LOAD%\reports\consulta.html" ConsultarUser
goto after_run

:load_rag
call :load_check
if errorlevel 1 goto after_run
"%VENV_LOCUST%" -f "%LOAD%\locustfile.py" --headless -u 20 -r 5 --run-time 1m --csv "%LOAD%\reports\rag" --html "%LOAD%\reports\rag.html" RagUser
goto after_run

:load_all
call :load_check
if errorlevel 1 goto after_run
echo.
echo [carga] Ejecutando Crear...
"%VENV_LOCUST%" -f "%LOAD%\locustfile.py" --headless -u 50 -r 10 --run-time 1m --csv "%LOAD%\reports\crear" --html "%LOAD%\reports\crear.html" CrearUser
echo.
echo [carga] Ejecutando Consulta...
"%VENV_LOCUST%" -f "%LOAD%\locustfile.py" --headless -u 100 -r 20 --run-time 1m --csv "%LOAD%\reports\consulta" --html "%LOAD%\reports\consulta.html" ConsultarUser
echo.
echo [carga] Ejecutando RAG...
"%VENV_LOCUST%" -f "%LOAD%\locustfile.py" --headless -u 20 -r 5 --run-time 1m --csv "%LOAD%\reports\rag" --html "%LOAD%\reports\rag.html" RagUser
goto after_run

:after_run
echo.
echo ----------------------------------------
choice /c sn /n /m "Otro test? (s/n): "
if errorlevel 2 goto end
goto menu

:end
echo.
endlocal
exit /b 0
