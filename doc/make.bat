@echo OFF
REM Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)

REM find python
where /q python
if errorlevel 1 (
	echo.Python cannot be found. Ensure it is installed and placed in your PATH.
    exit /b
)

REM default html builder
set builder=%1
if "%builder%" == "" (
	set builder=html
)

REM invoke build
python -m sphinx -M %builder% %~dp0 %~dp0_build -E -a
