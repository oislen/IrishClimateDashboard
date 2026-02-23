:: call powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
:: uv init IrishClimateDashboard
call uv add -r ..\..\requirements.txt --link-mode=copy