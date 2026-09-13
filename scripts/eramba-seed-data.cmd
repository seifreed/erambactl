@echo off
setlocal

if "%PYTHON%"=="" set "PYTHON=py -3.14"

%PYTHON% -c "import sys; sys.argv[0] = 'eramba-seed-data'; from erambactl.seed import main; raise SystemExit(main())" %*
