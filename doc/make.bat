@echo OFF
setlocal
REM Copyright Sphinx Confluence Builder Contributors (AUTHORS)

REM find python
where /q python
if errorlevel 1 (
	echo.Python cannot be found. Ensure it is installed and placed in your PATH.
    exit /b
)

REM find root directory to invoke in, to ensure the version of the project can
REM be extracted from the source
for %%i in ("%~dp0..") do set "root_dir=%%~fi"

REM default html builder
set builder=%1
if "%builder%" == "" (
	set builder=html
)

REM invoke build
pushd %root_dir%
set errorlevel=
python -m sphinx -M %builder% %~dp0 %~dp0_build -E -a -W
popd

exit /b %errorlevel%
