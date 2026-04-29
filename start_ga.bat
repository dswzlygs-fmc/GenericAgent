@echo off
REM 一键启动 GenericAgent（双击即可）
title Starting GenericAgent...
:: 强制 UTF-8 编码 + TrueType 字体，避免中文乱码
chcp 65001 >nul
reg add "HKCU\Console" /v "FaceName" /t REG_SZ /d "Consolas" /f >nul 2>nul

echo [1/3] 初始化 Conda 环境...
call F:\anaconda3\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: 无法初始化 Conda，请确认 Anaconda 安装路径。
    pause
    exit /b 1
)

echo [2/3] 激活 agent 环境...
call conda activate agent
if errorlevel 1 (
    echo ERROR: 无法激活 agent 环境，请确认环境名称是否正确。
    pause
    exit /b 1
)

echo [3/3] 启动 GenericAgent...
cd /d F:\Code\GenericAgent
python launch.pyw --wechat

echo GenericAgent 已启动（窗口已隐藏，请查看系统托盘或任务管理器）。
REM 如需保持窗口可去掉下一行注释
REM pause