@echo off
echo ========================================
echo Podman Container Cleanup
echo ========================================

echo.
echo Current running containers:
podman ps

echo.
echo [1/4] Stopping compose services...
cd C:\mygit\e-commerce\services
podman-compose -f podman-compose-infra.yaml down

echo.
echo [2/4] Killing any remaining containers...
for /f "tokens=*" %%i in ('podman ps -q') do podman kill %%i

echo.
echo [3/4] Removing stopped containers...
for /f "tokens=*" %%i in ('podman ps -aq') do podman rm -f %%i

echo.
echo [4/4] Cleanup complete!
echo.
echo Remaining containers:
podman ps -a

pause