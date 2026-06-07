@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   mcp-exif installer
echo   ExifTool MCP Server setup for Claude Desktop / Claude Code
echo ============================================================
echo.
echo This script will:
echo   1. Check for Python 3.10+ and Perl (or a standalone exiftool.exe)
echo   2. Create a virtual environment in .venv
echo   3. Install Python dependencies from requirements.txt
echo   4. Create a .env file from .env.example (if missing)
echo   5. Print the config snippet to wire this server into Claude
echo.
echo Requirements before you continue:
echo   - Python 3.10 or newer (https://www.python.org/downloads/)
echo   - ExifTool (https://exiftool.org/) - either:
echo       a) the Perl script + Perl on PATH (e.g. Strawberry Perl), or
echo       b) the standalone exiftool(-k).exe renamed to exiftool.exe
echo.
pause

rem ------------------------------------------------------------
rem 1. Check Python
rem ------------------------------------------------------------
echo.
echo [1/5] Checking for Python...
set PYTHON_CMD=

rem Prefer the official "py" launcher - "python" on PATH is sometimes just the
rem Microsoft Store app-execution-alias stub, which prints a message but
rem doesn't actually run Python.
for /f "delims=" %%i in ('py -3 --version 2^>^&1') do set PYCHECK=%%i
echo %PYCHECK% | findstr /b /c:"Python " >nul
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    set PYVEROUT=%PYCHECK%
) else (
    for /f "delims=" %%i in ('python --version 2^>^&1') do set PYCHECK=%%i
    echo %PYCHECK% | findstr /b /c:"Python " >nul
    if not errorlevel 1 (
        set PYTHON_CMD=python
        set PYVEROUT=%PYCHECK%
    )
)

if "%PYTHON_CMD%"=="" (
    echo ERROR: Could not find a working Python 3 interpreter.
    echo.
    echo If you have Python installed but see a message like
    echo "Python was not found; run without arguments to install from
    echo the Microsoft Store..." then Windows' app-execution-alias is
    echo shadowing your real install. Disable it via:
    echo   Settings ^> Apps ^> Advanced app settings ^> App execution aliases
    echo   ^(turn off the python.exe / python3.exe entries^)
    echo Then re-run this script, or install Python from
    echo https://www.python.org/downloads/ ^(check "Add python.exe to PATH"^).
    goto :fail
)

for /f "tokens=2" %%v in ("%PYVEROUT%") do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PYMAJOR=%%a
    set PYMINOR=%%b
)
echo Found %PYVEROUT% via "%PYTHON_CMD%"
if %PYMAJOR% LSS 3 goto :pyold
if %PYMAJOR% EQU 3 if %PYMINOR% LSS 10 goto :pyold
goto :pyok

:pyold
echo ERROR: Python 3.10+ is required, found %PYVER%.
goto :fail

:pyok

rem ------------------------------------------------------------
rem 2. Check for ExifTool / Perl (informational - not fatal)
rem ------------------------------------------------------------
echo.
echo [2/5] Checking for ExifTool / Perl...
where exiftool >nul 2>nul
if not errorlevel 1 (
    echo Found exiftool on PATH - you can set EXIFTOOL_PATH=exiftool in .env
) else (
    where perl >nul 2>nul
    if not errorlevel 1 (
        echo Found Perl on PATH. If you have the ExifTool Perl script, set
        echo EXIFTOOL_PATH=perl C:/path/to/exiftool in your .env file.
    ) else (
        echo WARNING: Neither "exiftool" nor "perl" was found on PATH.
        echo You still need to install ExifTool to use this server:
        echo   - Standalone Windows exe: https://exiftool.org/
        echo       ^(rename exiftool^(-k^).exe to exiftool.exe and put it on PATH^)
        echo   - Or install Strawberry Perl: https://strawberryperl.com/
        echo     and use the ExifTool Perl script.
        echo You can continue installing now and configure EXIFTOOL_PATH later.
    )
)

rem ------------------------------------------------------------
rem 3. Create virtual environment
rem ------------------------------------------------------------
echo.
echo [3/5] Setting up virtual environment...
if exist ".venv\Scripts\python.exe" (
    echo .venv already exists, skipping creation.
) else (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        goto :fail
    )
)

rem ------------------------------------------------------------
rem 4. Install dependencies
rem ------------------------------------------------------------
echo.
echo [4/5] Installing Python dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. See output above for details.
    goto :fail
)

rem ------------------------------------------------------------
rem 5. Create .env from template
rem ------------------------------------------------------------
echo.
echo [5/5] Configuring environment...
if exist ".env" (
    echo .env already exists, leaving it untouched.
) else (
    copy /y ".env.example" ".env" >nul
    echo Created .env from .env.example
    echo IMPORTANT: open .env and set EXIFTOOL_PATH to match your setup, e.g.
    echo   EXIFTOOL_PATH=exiftool
    echo   EXIFTOOL_PATH=perl C:/Tools/exiftool-master/exiftool
    echo   EXIFTOOL_PATH=C:/Tools/exiftool-master/exiftool.exe
)

echo.
echo ============================================================
echo   Install complete^^!
echo ============================================================
echo.
echo Next steps:
echo   1. Edit .env and confirm EXIFTOOL_PATH is correct for your machine.
echo   2. Wire the server into Claude Desktop by adding this to
echo      claude_desktop_config.json ("mcpServers" section):
echo.
echo      "exiftool": {
echo        "command": "%CD%\.venv\Scripts\python.exe",
echo        "args": ["%CD%\server.py"]
echo      }
echo.
echo   - Or for Claude Code (CLI), run:
echo      claude mcp add exiftool "%CD%\.venv\Scripts\python.exe" "%CD%\server.py"
echo.
echo See CLAUDE.md for full documentation.
echo.
pause
exit /b 0

:fail
echo.
echo Installation did not complete. Resolve the issue above and re-run install.bat.
pause
exit /b 1
