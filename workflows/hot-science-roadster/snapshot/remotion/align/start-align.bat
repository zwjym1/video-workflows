@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
where node >nul 2>nul || (echo 没找到 Node.js，请先安装 https://nodejs.org （选 LTS 版）& pause & exit /b 1)
if not exist node_modules (
  echo 第一次运行：正在安装依赖，需要几分钟……
  call npm install || (echo 依赖安装失败 & pause & exit /b 1)
)
call npm run align
pause
