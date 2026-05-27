@echo off
setlocal EnableDelayedExpansion
set "ROOT=%~dp0"
set "VENV_PY=%ROOT%.venv-test\Scripts\python.exe"
set "TESTS=%ROOT%microservicios"

if not exist "%VENV_PY%" (
    echo No existe %VENV_PY%
    echo Crea el venv primero:
    echo     py -3.13 -m venv .venv-test
    echo     .venv-test\Scripts\python.exe -m pip install fastapi==0.115.12 pydantic==2.11.1 "pydantic[email]" httpx==0.28.1 pytest==9.0.3 pytest-asyncio pytest-cov python-jose passlib bcrypt python-multipart asyncpg sqlalchemy
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
echo   [1] Todos los tests
echo   [2] Todos los tests + coverage
echo   [3] Un microservicio
echo   [4] Solo modelos Pydantic ^(RF9^)
echo   [5] Filtrar por nombre ^(-k^)
echo   [0] Salir
echo ========================================
choice /c 012345 /n /m "Elegir [0-5]: "
set "OPT=!errorlevel!"

if "!OPT!"=="1" goto end
if "!OPT!"=="2" goto run_all
if "!OPT!"=="3" goto run_cov
if "!OPT!"=="4" goto menu_service
if "!OPT!"=="5" goto run_models
if "!OPT!"=="6" goto run_filter
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
