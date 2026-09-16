@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ==============================================================================
echo    FARMACIAS SAO JOAO - DASHBOARD GERENCIAL DIGITAL ^& FIGITAL 360°
echo    Rotina Matinal de Atualizacao Automatica
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/5] Carregando Metas Oficiais de 2026 (base Gerencial.xlsx)...
python load_metas_gerencial.py
if errorlevel 1 (
    echo [ERRO] Falha ao carregar metas.
    pause
    exit /b 1
)

echo.
echo [2/5] Extraindo Vendas, Cupons e Margens do Qlik Cloud (SenseCloud)...
python extract_qlik_cloud_gerencial.py
if errorlevel 1 (
    echo [AVISO] Falha temporaria no Qlik Cloud. Utilizando snapshot consolidado.
)

echo.
echo [3/5] Atualizando Metricas de Trafego e Conversao (GA4 / Supermetrics)...
python connectors_analytics.py

echo.
echo [4/5] Processando Motor Analitico e Reconciliacao Real vs Meta...
python process_gerencial_analytics.py
if errorlevel 1 (
    echo [ERRO] Falha no processamento analitico.
    pause
    exit /b 1
)

echo.
echo [5/5] Compilando Dashboard Executivo Apple/FSJ Design (index.html)...
python build_dashboard_gerencial.py
if errorlevel 1 (
    echo [ERRO] Falha ao compilar dashboard.
    pause
    exit /b 1
)

echo.
echo [6/6] Publicando Atualizacoes no GitHub Pages...
git add index.html data/*.json *.py *.png >nul 2>&1
git diff --staged --quiet
if errorlevel 1 (
    git commit -m "Auto-sync Dashboard Gerencial (%date% %time%)"
    git push github main --quiet
    git push github HEAD:gh-pages --quiet
    echo Atualizacoes enviadas para o GitHub Pages com sucesso!
) else (
    echo Nenhum arquivo alterado para publicacao.
)

echo.
echo ==============================================================================
echo    ATUALIZACAO CONCLUIDA COM SUCESSO!
echo    Local : %~dp0index.html
echo    Online: https://lukasg64-png.github.io/dashboard-gerencial-digital/
echo ==============================================================================
echo.

start "" "%~dp0index.html"
