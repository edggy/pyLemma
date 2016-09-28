REM python main.py "$(FULL_CURRENT_PATH)"

@echo off

set COMMAND="%~1"

SHIFT

set ARGS=

:loop
if "%~1" == "" goto end
set ARGS=%ARGS% %1
SHIFT
goto loop


:end

%COMMAND% %ARGS% > tmp
"C:\Program Files (x86)\Notepad++\notepad++.exe" tmp
