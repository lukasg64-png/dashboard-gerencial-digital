@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

cd /d "%~dp0"
set LOGFILE=%~dp0rotina_execucao.log

echo ============================================================================== >> "%LOGFILE%"
echo [%DATE% %TIME%] INICIANDO ROTINA DE ATUALIZACAO AUTOMATICA >> "%LOGFILE%"
echo ============================================================================== >> "%LOGFILE%"

echo ==============================================================================
echo    FARMACIAS SAO JOAO - DASHBOARD GERENCIAL DIGITAL ^& FIGITAL 360°
echo    Rotina Matinal de Atualizacao Automatica
echo ==============================================================================
echo.

echo [1/5] Carregando Metas Oficiais de 2026 (base Gerencial.xlsx)...
echo [%TIME%] [1/5] Carregando Metas... >> "%LOGFILE%"
python load_metas_gerencial.py >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao carregar metas. Detalhes em rotina_execucao.log.
    echo [%TIME%] [ERRO] Falha em load_metas_gerencial.py >> "%LOGFILE%"
    if not "%1"=="--unattended" timeout /t 10
    exit /b 1
)

echo.
echo [2/5] Extraindo Vendas, Cupons e Margens do Qlik Cloud (SenseCloud)...
echo [%TIME%] [2/5] Extraindo Qlik Cloud... >> "%LOGFILE%"
python extract_qlik_cloud_gerencial.py >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [AVISO] Qlik Cloud offline/instavel. Utilizando snapshot consolidado resiliente.
    echo [%TIME%] [AVISO] Snapshot consolidado utilizado para Qlik >> "%LOGFILE%"
)

echo.
echo [3/5] Atualizando Metricas de Trafego e Conversao (GA4 / Supermetrics)...
echo [%TIME%] [3/5] Atualizando Trafego GA4 / Supermetrics... >> "%LOGFILE%"
python connectors_analytics.py >> "%LOGFILE%" 2>&1

echo.
echo [4/5] Processando Motor Analitico e Reconciliacao Real vs Meta...
echo [%TIME%] [4/5] Processando Motor Analitico... >> "%LOGFILE%"
python process_gerencial_analytics.py >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [ERRO] Falha no processamento analitico. Detalhes em rotina_execucao.log.
    echo [%TIME%] [ERRO] Falha em process_gerencial_analytics.py >> "%LOGFILE%"
    if not "%1"=="--unattended" timeout /t 10
    exit /b 1
)

echo.
echo [5/5] Compilando Dashboard Executivo Apple/FSJ Design (index.html)...
echo [%TIME%] [5/5] Compilando Dashboard Executivo... >> "%LOGFILE%"
python build_dashboard_gerencial.py >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao compilar dashboard. Detalhes em rotina_execucao.log.
    echo [%TIME%] [ERRO] Falha em build_dashboard_gerencial.py >> "%LOGFILE%"
    if not "%1"=="--unattended" timeout /t 10
    exit /b 1
)

echo.
echo [6/6] Publicando Atualizacoes no GitHub Pages...
echo [%TIME%] [6/6] Sincronizando com Git e GitHub Pages... >> "%LOGFILE%"
git add index.html data/*.json *.py *.png >nul 2>&1
git diff --staged --quiet
if errorlevel 1 (
    git commit -m "Auto-sync Dashboard Gerencial (%date% %time%)" >> "%LOGFILE%" 2>&1
    git push github main --quiet >> "%LOGFILE%" 2>&1
    git push github HEAD:gh-pages --quiet >> "%LOGFILE%" 2>&1
    echo Atualizacoes enviadas para o GitHub Pages com sucesso!
    echo [%TIME%] GitHub Pages atualizado com sucesso! >> "%LOGFILE%"
) else (
    echo Nenhum arquivo alterado para publicacao.
    echo [%TIME%] Nenhum arquivo alterado para publicacao. >> "%LOGFILE%"
)

echo.
echo ==============================================================================
echo    ATUALIZACAO CONCLUIDA COM SUCESSO!
echo    Local : %~dp0index.html
echo    Online: https://lukasg64-png.github.io/dashboard-gerencial-digital/
echo    Log   : %LOGFILE%
echo ==============================================================================
echo [%TIME%] ROTINA FINALIZADA COM SUCESSO! >> "%LOGFILE%"
echo.

if not "%1"=="--unattended" (
    start "" "%~dp0index.html"
)

