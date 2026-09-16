"""
build_dashboard_gerencial.py — Compilador do Dashboard Gerencial Digital & Figital.
Gera a aplicação web executiva completa 'index.html' autônoma, responsiva e ultra-veloz.
Design System: Apple Human Interface + Identidade Visual Farmácias São João.
"""
import os
import sys
import time
import json

if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_JSON_PATH = os.path.join(DATA_DIR, 'dashboard_gerencial_data.json')
OUTPUT_HTML = os.path.join(BASE_DIR, 'index.html')

def build():
    t0 = time.time()
    print("=" * 70)
    print("  COMPILANDO DASHBOARD GERENCIAL DIGITAL & FIGITAL — APPLE/FSJ DESIGN")
    print("=" * 70)

    if not os.path.exists(DATA_JSON_PATH):
        print("Arquivo de dados não encontrado. Executando process_gerencial_analytics.py...")
        import process_gerencial_analytics
        process_gerencial_analytics.main()

    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data_json_str = f.read()

    dash_data = json.loads(data_json_str)
    kpis = dash_data.get('kpis', {})
    charts = dash_data.get('charts', {})
    proj = dash_data.get('projecoes', {})
    origens = dash_data.get('origens_trafego', [])
    data_corte = dash_data.get('data_corte', '01 a 15/09/2026')
    atualizacao = dash_data.get('atualizacao', time.strftime('%Y-%m-%d %H:%M:%S'))

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard Gerencial — Canais Digitais & Figital | Farmácias São João</title>
  
  <!-- Apple & São João Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Chart.js 4 & DataLabels Plugin -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

  <style>
    /* ==========================================================================
       FARMÁCIAS SÃO JOÃO — APPLE DESIGN SYSTEM & THEME TOKENS
       ========================================================================== */
    :root {{
      --fsj-blue: #0056b3;
      --fsj-blue-dark: #003875;
      --fsj-blue-light: #0077ff;
      --fsj-blue-gradient: linear-gradient(135deg, #0056b3 0%, #0077ff 100%);
      --fsj-accent: #ff4757;
      
      --bg-main: #f4f6fb;
      --bg-sidebar: #0056b3;
      --bg-card: #ffffff;
      --bg-card-subtle: #f8fafc;
      --bg-card-hover: #ffffff;
      --border-card: rgba(0, 0, 0, 0.06);
      
      --text-primary: #1e293b;
      --text-secondary: #64748b;
      --text-muted: #94a3b8;
      
      --badge-green-bg: #dcfce7;
      --badge-green-text: #15803d;
      --badge-red-bg: #fee2e2;
      --badge-red-text: #b91c1c;
      --badge-blue-bg: #e0f2fe;
      --badge-blue-text: #0369a1;
      --badge-purple-bg: #f3e8ff;
      --badge-purple-text: #7e22ce;
      
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 10px 25px rgba(0, 86, 179, 0.08);
      
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 18px;
      --radius-pill: 9999px;
      
      --transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    [data-theme="dark"] {{
      --bg-main: #0b111e;
      --bg-sidebar: #070e1b;
      --bg-card: #151f32;
      --bg-card-subtle: #1c283f;
      --bg-card-hover: #1e2c46;
      --border-card: rgba(255, 255, 255, 0.07);
      
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      
      --badge-green-bg: rgba(34, 197, 94, 0.15);
      --badge-green-text: #4ade80;
      --badge-red-bg: rgba(239, 68, 68, 0.15);
      --badge-red-text: #f87171;
      --badge-blue-bg: rgba(56, 189, 248, 0.15);
      --badge-blue-text: #38bdf8;
      --badge-purple-bg: rgba(168, 85, 247, 0.15);
      --badge-purple-text: #c084fc;
      
      --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.25);
      --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.4);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      overflow-x: hidden;
      transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* ==========================================================================
       SIDEBAR NAVEGAÇÃO — ESTILO FARMÁCIAS SÃO JOÃO
       ========================================================================== */
    .sidebar {{
      width: 78px;
      background: var(--fsj-blue-gradient);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 0;
      position: sticky;
      top: 0;
      height: 100vh;
      z-index: 100;
      box-shadow: 4px 0 20px rgba(0, 56, 117, 0.15);
      transition: var(--transition);
    }}

    .sidebar-brand {{
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.18);
      backdrop-filter: blur(10px);
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: white;
      margin-bottom: 36px;
      font-weight: 800;
      font-size: 11px;
      letter-spacing: 0.5px;
      border: 1px solid rgba(255, 255, 255, 0.25);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}

    .sidebar-brand span:first-child {{
      font-size: 13px;
      line-height: 1;
    }}
    .sidebar-brand span:last-child {{
      font-size: 8px;
      opacity: 0.9;
    }}

    .nav-items {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      width: 100%;
      align-items: center;
    }}

    .nav-btn {{
      width: 50px;
      height: 50px;
      border-radius: 16px;
      border: none;
      background: transparent;
      color: rgba(255, 255, 255, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      position: relative;
      transition: var(--transition);
    }}

    .nav-btn:hover {{
      color: #ffffff;
      background: rgba(255, 255, 255, 0.15);
      transform: scale(1.05);
    }}

    .nav-btn.active {{
      color: var(--fsj-blue);
      background: #ffffff;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }}

    [data-theme="dark"] .nav-btn.active {{
      color: #0b111e;
      background: #ffffff;
    }}

    .nav-btn svg {{
      width: 24px;
      height: 24px;
      stroke-width: 2.2;
    }}

    .sidebar-spacer {{
      flex: 1;
    }}

    /* ==========================================================================
       MAIN CONTENT CONTAINER
       ========================================================================== */
    .main-wrapper {{
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      padding: 24px 32px 48px;
      gap: 24px;
    }}

    /* Header Bar */
    .top-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      background: var(--bg-card);
      padding: 18px 24px;
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      box-shadow: var(--shadow-sm);
    }}

    .header-titles h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .header-titles h1 .tag-figital {{
      font-size: 11px;
      font-family: 'Inter', sans-serif;
      font-weight: 700;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      color: white;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}

    .header-titles p {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-top: 3px;
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .period-select-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      padding: 8px 14px;
      border-radius: var(--radius-pill);
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
    }}

    .period-select-box svg {{
      color: var(--fsj-blue-light);
    }}

    .period-select {{
      border: none;
      background: transparent;
      color: inherit;
      font-size: 13px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }}

    .theme-toggle-btn, .action-btn {{
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      width: 40px;
      height: 40px;
      border-radius: var(--radius-pill);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      color: var(--text-primary);
      transition: var(--transition);
    }}

    .theme-toggle-btn:hover, .action-btn:hover {{
      background: var(--bg-card-hover);
      transform: scale(1.05);
      border-color: var(--fsj-blue-light);
    }}

    /* ==========================================================================
       VIEWS SWITCHING
       ========================================================================== */
    .view-panel {{
      display: none;
      flex-direction: column;
      gap: 24px;
      animation: fadeIn 0.3s ease;
    }}

    .view-panel.active {{
      display: flex;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ==========================================================================
       VISÃO 1: TOP SUMMARY CARDS (E-COMMERCE, DIGITAIS, TELEVENDAS, FIGITAL)
       ========================================================================== */
    .top-hero-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 18px;
    }}

    @media (max-width: 1400px) {{
      .top-hero-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    @media (max-width: 768px) {{
      .top-hero-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .hero-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 22px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: relative;
      overflow: hidden;
      transition: var(--transition);
    }}

    .hero-card:hover {{
      box-shadow: var(--shadow-md);
      transform: translateY(-2px);
    }}

    .hero-card.highlight-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--fsj-blue-gradient);
    }}

    .hero-card.figital-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(135deg, #8b5cf6, #3b82f6);
    }}

    .hero-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .hero-title-group {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .hero-title-group h3 {{
      font-size: 15px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .hero-subtitle {{
      font-size: 12px;
      color: var(--text-secondary);
    }}

    .hero-part-badge {{
      font-size: 12px;
      font-weight: 700;
      color: var(--fsj-blue);
      background: var(--badge-blue-bg);
      padding: 4px 10px;
      border-radius: var(--radius-pill);
    }}

    [data-theme="dark"] .hero-part-badge {{
      color: #38bdf8;
    }}

    .hero-val-group {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .hero-main-val {{
      font-family: 'Outfit', sans-serif;
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -1px;
    }}

    .hero-meta-mes {{
      font-size: 13px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .hero-meta-mes strong {{
      color: var(--text-primary);
      font-weight: 700;
    }}

    /* Green / Red Meta Pill Box */
    .hero-meta-pill {{
      background: var(--badge-green-bg);
      color: var(--badge-green-text);
      border-radius: var(--radius-md);
      padding: 10px 14px;
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
    }}

    .hero-meta-pill.negative {{
      background: var(--badge-red-bg);
      color: var(--badge-red-text);
    }}

    .hero-meta-pill span strong {{
      font-weight: 800;
    }}

    /* Sub KPI Indicators (Evo YoY, Cresc MoM, Rentabilidade) */
    .hero-sub-indicators {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-secondary);
      padding: 2px 4px;
    }}

    .indicator-item strong {{
      color: var(--text-primary);
      font-weight: 700;
    }}

    .val-positive {{
      color: #16a34a !important;
      font-weight: 700;
    }}

    .val-negative {{
      color: #dc2626 !important;
      font-weight: 700;
    }}

    /* Ticket Médio Box */
    .hero-tkm-box {{
      background: var(--badge-red-bg);
      color: var(--badge-red-text);
      border-radius: var(--radius-md);
      padding: 8px 12px;
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 600;
    }}

    .hero-tkm-box.positive {{
      background: var(--badge-green-bg);
      color: var(--badge-green-text);
    }}

    /* ==========================================================================
       DETAILED CHANNEL CARDS (SITE, APP, MKP, FIGITAL, SITE+APP)
       ========================================================================== */
    .channels-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
    }}

    @media (max-width: 1200px) {{
      .channels-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .channel-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .channel-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 1px solid var(--border-card);
      padding-bottom: 12px;
    }}

    .channel-header h4 {{
      font-size: 18px;
      font-weight: 800;
      font-family: 'Outfit', sans-serif;
    }}

    .channel-venda-sub {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .channel-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}

    .channel-table th {{
      text-align: right;
      color: var(--text-muted);
      font-weight: 600;
      padding: 6px 4px;
      border-bottom: 1px solid var(--border-card);
    }}

    .channel-table th:first-child {{
      text-align: left;
    }}

    .channel-table td {{
      padding: 8px 4px;
      text-align: right;
      border-bottom: 1px solid var(--border-card);
      color: var(--text-primary);
      font-weight: 600;
    }}

    .channel-table td:first-child {{
      text-align: left;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .channel-table tr:last-child td {{
      border-bottom: none;
    }}

    /* Bottom Summary Bar (Site & App) */
    .combined-bar {{
      grid-column: 1 / -1;
      background: var(--bg-card-subtle);
      border-radius: var(--radius-md);
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      border: 1px dashed var(--border-card);
    }}

    .combined-title {{
      font-weight: 800;
      font-size: 16px;
      font-family: 'Outfit', sans-serif;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .combined-metrics {{
      display: flex;
      gap: 24px;
      flex-wrap: wrap;
      font-size: 13px;
    }}

    /* ==========================================================================
       VISÃO 2: TENDÊNCIAS & DESVIOS DIÁRIOS (CHARTS)
       ========================================================================== */
    .filter-pills-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-card);
      padding: 14px 20px;
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      flex-wrap: wrap;
      gap: 12px;
    }}

    .pill-group {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .pill-btn {{
      padding: 8px 18px;
      border-radius: var(--radius-pill);
      border: 1px solid var(--border-card);
      background: var(--bg-card-subtle);
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: var(--transition);
    }}

    .pill-btn:hover {{
      background: var(--bg-card-hover);
      color: var(--text-primary);
    }}

    .pill-btn.active {{
      background: var(--fsj-blue-light);
      color: white;
      border-color: var(--fsj-blue-light);
      box-shadow: 0 4px 10px rgba(0, 119, 255, 0.25);
    }}

    .chart-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .chart-header h3 {{
      font-size: 16px;
      font-weight: 800;
      font-family: 'Outfit', sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .chart-legend-custom {{
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}

    .chart-container {{
      position: relative;
      width: 100%;
      height: 285px;
    }}

    /* ==========================================================================
       VISÃO 3: TRÁFEGO, CONVERSÃO E ORIGENS
       ========================================================================== */
    .traffic-table-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 24px;
      box-shadow: var(--shadow-sm);
    }}

    .traffic-table-card h3 {{
      font-size: 16px;
      font-weight: 800;
      font-family: 'Outfit', sans-serif;
      margin-bottom: 16px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}

    .data-table th {{
      text-align: right;
      color: var(--text-muted);
      font-weight: 600;
      padding: 10px 12px;
      border-bottom: 2px solid var(--border-card);
      background: var(--bg-card-subtle);
    }}

    .data-table th:first-child {{
      text-align: left;
      border-radius: var(--radius-sm) 0 0 var(--radius-sm);
    }}

    .data-table th:last-child {{
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    }}

    .data-table td {{
      padding: 12px;
      text-align: right;
      border-bottom: 1px solid var(--border-card);
      color: var(--text-primary);
      font-weight: 500;
    }}

    .data-table td:first-child {{
      text-align: left;
      font-weight: 700;
    }}

    /* ==========================================================================
       VISÃO 4: PROJEÇÃO DE FECHAMENTO & SIMULADOR
       ========================================================================== */
    .projection-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
    }}

    @media (max-width: 992px) {{
      .projection-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .proj-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .proj-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-card);
      padding-bottom: 12px;
    }}

    .proj-metrics-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      text-align: center;
    }}

    .proj-box {{
      background: var(--bg-card-subtle);
      border-radius: var(--radius-md);
      padding: 12px 8px;
    }}

    .proj-box .lbl {{
      font-size: 11px;
      color: var(--text-secondary);
      font-weight: 600;
    }}

    .proj-box .val {{
      font-size: 18px;
      font-weight: 800;
      margin-top: 4px;
      font-family: 'Outfit', sans-serif;
    }}

    /* Progress bar */
    .progress-track {{
      background: var(--bg-card-subtle);
      height: 12px;
      border-radius: var(--radius-pill);
      overflow: hidden;
      margin-top: 8px;
    }}

    .progress-fill {{
      height: 100%;
      background: var(--fsj-blue-gradient);
      border-radius: var(--radius-pill);
      transition: width 0.8s ease;
    }}
  </style>
</head>
<body>

  <!-- SIDEBAR NAVEGAÇÃO -->
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span>FSJ</span>
      <span>DIGITAL</span>
    </div>
    <div class="nav-items">
      <!-- Visão 1: Visão Geral -->
      <button class="nav-btn active" data-view="view-geral" title="Visão Geral & Cards Executivos">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
      </button>

      <!-- Visão 2: Tendências & Desvios Diários -->
      <button class="nav-btn" data-view="view-desvios" title="Tendências & Desvios Diários">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
        </svg>
      </button>

      <!-- Visão 3: Tráfego e Conversão -->
      <button class="nav-btn" data-view="view-trafego" title="Tráfego, Conversão e Origens">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </button>

      <!-- Visão 4: Projeção & Run Rate -->
      <button class="nav-btn" data-view="view-projecoes" title="Projeção de Fechamento & Fechamento Mês">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
        </svg>
      </button>
    </div>
    <div class="sidebar-spacer"></div>
  </aside>

  <!-- MAIN WRAPPER -->
  <main class="main-wrapper">
    <!-- Top Header -->
    <header class="top-header">
      <div class="header-titles">
        <h1>
          Dashboard Gerencial — Canais Digitais
          <span class="tag-figital">+ Figital</span>
        </h1>
        <p>Acompanhamento Oficial de Metas, Venda Efetiva, Tráfego e Rentabilidade | Atualizado: {atualizacao}</p>
      </div>
      <div class="header-controls">
        <div class="period-select-box">
          <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          <select class="period-select" id="periodFilter">
            <option value="mtd" selected>01/09/2026 a 15/09/2026 (D-1 Oficial)</option>
            <option value="d1">Ontem: 15/09/2026 (Fechamento)</option>
            <option value="full">Setembro/2026 (Mês Completo)</option>
          </select>
        </div>
        <button class="theme-toggle-btn" id="themeBtn" title="Alternar Modo Escuro/Claro">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- ====================================================================
         VISÃO 1: VISÃO GERAL & CARDS EXECUTIVOS
         ==================================================================== -->
    <section class="view-panel active" id="view-geral">
      <!-- 4 Top Hero Cards -->
      <div class="top-hero-grid">
        <!-- Card 1: E-COMMERCE TOTAL -->
        <div class="hero-card highlight-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>E-Commerce</h3>
              <span class="hero-subtitle">Venda Efetiva</span>
            </div>
            <span class="hero-part-badge">Part: {kpis['ecommerce_total']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val">R$ 30.436 Mi</span>
            <span class="hero-meta-mes">Meta Mês: <strong>55.845 Mi</strong></span>
          </div>
          <div class="hero-meta-pill">
            <span>Meta: <strong>R$ 28,6 Mi</strong></span>
            <span>Desvio (%): <strong class="val-positive">+{kpis['ecommerce_total']['desvio_venda_pct']:.2f}%</strong></span>
            <span>Desvio (R$): <strong>+1,79 Mi</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="val-positive">⇑ 65,1%</strong></span>
            <span class="indicator-item">Crescimento: <strong class="val-positive">⇑ 4,6%</strong></span>
          </div>
          <div class="hero-tkm-box">
            <span>Ticket Médio: <strong>120,52</strong></span>
            <span>Meta: <strong>131,25</strong></span>
            <span>Desvio (%): <strong class="val-negative">-8,17%</strong></span>
            <span>Desvio (R$): <strong>-10,73</strong></span>
          </div>
        </div>

        <!-- Card 2: CANAIS DIGITAIS -->
        <div class="hero-card highlight-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Canais Digitais</h3>
              <span class="hero-subtitle">Site + App + Marketplace</span>
            </div>
            <span class="hero-part-badge">Part: {kpis['canais_digitais']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val">R$ 29.766 Mi</span>
            <span class="hero-meta-mes">Meta Mês: <strong>54.745 Mi</strong></span>
          </div>
          <div class="hero-meta-pill">
            <span>Meta: <strong>R$ 28,084 Mi</strong></span>
            <span>Desvio (%): <strong class="val-positive">+{kpis['canais_digitais']['desvio_venda_pct']:.2f}%</strong></span>
            <span>Desvio (R$): <strong>+1,682 Mi</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="val-positive">⇑ 63,7%</strong></span>
            <span class="indicator-item">Crescimento: <strong class="val-positive">⇑ 5,1%</strong></span>
            <span class="indicator-item">Rent. Op: <strong>20,47%</strong></span>
            <span class="indicator-item">Rent. DRE: <strong>25,50%</strong></span>
          </div>
          <div class="hero-tkm-box">
            <span>Ticket Médio: <strong>118,79</strong></span>
            <span>Meta: <strong>137,23</strong></span>
            <span>Desvio (%): <strong class="val-negative">-13,44%</strong></span>
            <span>Desvio (R$): <strong>-18,44</strong></span>
          </div>
        </div>

        <!-- Card 3: TELEVENDAS -->
        <div class="hero-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Televendas</h3>
              <span class="hero-subtitle">Venda Efetiva</span>
            </div>
            <span class="hero-part-badge">Part: {kpis['televendas']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val">R$ 670 K</span>
            <span class="hero-meta-mes">Meta Mês: <strong>1.100 Mi</strong></span>
          </div>
          <div class="hero-meta-pill">
            <span>Meta: <strong>564,30 Mil</strong></span>
            <span>Desvio (%): <strong class="val-positive">+{kpis['televendas']['desvio_venda_pct']:.2f}%</strong></span>
            <span>Desvio (R$): <strong>+105,61 Mil</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="val-positive">⇑ 169,4%</strong></span>
            <span class="indicator-item">Crescimento: <strong class="val-negative">⇓ -14,9%</strong></span>
          </div>
          <div class="hero-tkm-box positive">
            <span>Ticket Médio: <strong>339,71</strong></span>
            <span>Meta: <strong>113,29</strong></span>
            <span>Desvio (%): <strong class="val-positive">+199,85%</strong></span>
            <span>Desvio (R$): <strong>+226,42</strong></span>
          </div>
        </div>

        <!-- Card 4: FIGITAL (NOVO PILAR) -->
        <div class="hero-card figital-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Figital (Omnichannel)</h3>
              <span class="hero-subtitle">Lojas Integradas & Clique e Retire</span>
            </div>
            <span class="hero-part-badge" style="background: var(--badge-purple-bg); color: var(--badge-purple-text);">Part: {kpis['figital']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val">R$ 1.265 Mi</span>
            <span class="hero-meta-mes">Meta Mês: <strong>2.463 Mi</strong></span>
          </div>
          <div class="hero-meta-pill">
            <span>Meta: <strong>1.263 Mi</strong></span>
            <span>Desvio (%): <strong class="val-positive">+0,16%</strong></span>
            <span>Cupons: <strong>8,89 Mil</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="val-positive">⇑ 72,4%</strong></span>
            <span class="indicator-item">Crescimento: <strong class="val-positive">⇑ 12,3%</strong></span>
            <span class="indicator-item">Rent. Op: <strong>22,40%</strong></span>
          </div>
          <div class="hero-tkm-box positive">
            <span>Ticket Médio: <strong>142,30</strong></span>
            <span>Meta: <strong>140,00</strong></span>
            <span>Desvio (%): <strong class="val-positive">+1,64%</strong></span>
            <span>Desvio (R$): <strong>+2,30</strong></span>
          </div>
        </div>
      </div>

      <!-- Detalhamento por Canal (Site, App, Marketplace, Figital, Site+App) -->
      <div class="channels-grid">
        <!-- SITE -->
        <div class="channel-card">
          <div class="channel-header">
            <h4>SITE</h4>
            <span class="channel-venda-sub">Venda: <strong>4.804 Mi</strong> (Part: 1,07%)</span>
          </div>
          <table class="channel-table">
            <thead>
              <tr>
                <th>Métrica</th>
                <th>Real</th>
                <th>Meta</th>
                <th>Meta Mês</th>
                <th>Desvio %</th>
                <th>Evo.</th>
                <th>Cresc.</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Venda</td>
                <td>4.804 Mi</td>
                <td>7.435 Mi</td>
                <td>14.494 Mi</td>
                <td class="val-negative">-35,40%</td>
                <td class="val-negative">⇓ -11,7%</td>
                <td class="val-negative">⇓ -6,1%</td>
              </tr>
              <tr>
                <td>Qtd. NF</td>
                <td>30,949 Mil</td>
                <td>41,87 Mil</td>
                <td>81,65 Mil</td>
                <td class="val-negative">-26,08%</td>
                <td class="val-negative">⇓ -1,8%</td>
                <td class="val-negative">⇓ -5,3%</td>
              </tr>
              <tr>
                <td>Ticket M.</td>
                <td>155,21</td>
                <td>177,60</td>
                <td>177,51</td>
                <td class="val-negative">-12,61%</td>
                <td class="val-negative">⇓ -10,1%</td>
                <td class="val-negative">⇓ -0,8%</td>
              </tr>
              <tr>
                <td>Rent. Op.</td>
                <td>17,21%</td>
                <td>21,50%</td>
                <td>21,50%</td>
                <td class="val-negative">-4,29%</td>
                <td class="val-positive">⇑ 4,7%</td>
                <td class="val-positive">⇑ 5,4%</td>
              </tr>
              <tr>
                <td>Sessões</td>
                <td>1,26 Mi</td>
                <td>1,57 Mi</td>
                <td>3,07 Mi</td>
                <td class="val-negative">-19,80%</td>
                <td class="val-positive">⇑ 7,8%</td>
                <td class="val-positive">⇑ 2,7%</td>
              </tr>
              <tr>
                <td>Tx. Conv.</td>
                <td>2,45%</td>
                <td>2,66%</td>
                <td>2,66%</td>
                <td class="val-negative">-7,82%</td>
                <td class="val-negative">⇓ -8,9%</td>
                <td class="val-negative">⇓ -1,2%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- APP -->
        <div class="channel-card">
          <div class="channel-header">
            <h4>APP</h4>
            <span class="channel-venda-sub">Venda: <strong>16.226 Mi</strong> (Part: 3,60%)</span>
          </div>
          <table class="channel-table">
            <thead>
              <tr>
                <th>Métrica</th>
                <th>Real</th>
                <th>Meta</th>
                <th>Meta Mês</th>
                <th>Desvio %</th>
                <th>Evo.</th>
                <th>Cresc.</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Venda</td>
                <td>16.226 Mi</td>
                <td>13.308 Mi</td>
                <td>25.942 Mi</td>
                <td class="val-positive">+21,92%</td>
                <td class="val-positive">⇑ 88,8%</td>
                <td class="val-positive">⇑ 15,9%</td>
              </tr>
              <tr>
                <td>Qtd. NF</td>
                <td>117,975 Mil</td>
                <td>88,00 Mil</td>
                <td>171,55 Mil</td>
                <td class="val-positive">+34,06%</td>
                <td class="val-positive">⇑ 93,6%</td>
                <td class="val-positive">⇑ 18,5%</td>
              </tr>
              <tr>
                <td>Ticket M.</td>
                <td>137,54</td>
                <td>151,22</td>
                <td>151,22</td>
                <td class="val-negative">-9,05%</td>
                <td class="val-negative">⇓ -2,5%</td>
                <td class="val-negative">⇓ -2,2%</td>
              </tr>
              <tr>
                <td>Rent. Op.</td>
                <td>18,15%</td>
                <td>21,50%</td>
                <td>21,50%</td>
                <td class="val-negative">-3,35%</td>
                <td class="val-negative">⇓ -0,8%</td>
                <td class="val-positive">⇑ 5,0%</td>
              </tr>
              <tr>
                <td>Sessões</td>
                <td>1,00 Mi</td>
                <td>1,06 Mi</td>
                <td>2,07 Mi</td>
                <td class="val-negative">-5,14%</td>
                <td class="val-positive">⇑ 51,6%</td>
                <td class="val-negative">⇓ -7,7%</td>
              </tr>
              <tr>
                <td>Tx. Conv.</td>
                <td>11,74%</td>
                <td>8,31%</td>
                <td>8,31%</td>
                <td class="val-positive">+41,32%</td>
                <td class="val-positive">⇑ 27,7%</td>
                <td class="val-positive">⇑ 28,5%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- MARKETPLACE -->
        <div class="channel-card">
          <div class="channel-header">
            <h4>MARKETPLACE</h4>
            <span class="channel-venda-sub">Venda: <strong>8.737 Mi</strong> (Part: 1,94%)</span>
          </div>
          <table class="channel-table">
            <thead>
              <tr>
                <th>Métrica</th>
                <th>Real</th>
                <th>Meta</th>
                <th>Meta Mês</th>
                <th>Desvio %</th>
                <th>Evo.</th>
                <th>Cresc.</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Venda</td>
                <td>8.737 Mi</td>
                <td>7.340 Mi</td>
                <td>14.309 Mi</td>
                <td class="val-positive">+19,02%</td>
                <td class="val-positive">⇑ 110,8%</td>
                <td class="val-negative">⇓ -5,2%</td>
              </tr>
              <tr>
                <td>Qtd. NF</td>
                <td>101,64 Mil</td>
                <td>88,57 Mil</td>
                <td>172,67 Mil</td>
                <td class="val-positive">+14,76%</td>
                <td class="val-positive">⇑ 91,8%</td>
                <td class="val-negative">⇓ -3,7%</td>
              </tr>
              <tr>
                <td>Ticket M.</td>
                <td>85,95</td>
                <td>82,87</td>
                <td>82,87</td>
                <td class="val-positive">+3,72%</td>
                <td class="val-positive">⇑ 9,9%</td>
                <td class="val-negative">⇓ -1,5%</td>
              </tr>
              <tr>
                <td>Rent. Op.</td>
                <td>26,78%</td>
                <td>31,50%</td>
                <td>31,50%</td>
                <td class="val-negative">-4,72%</td>
                <td class="val-negative">⇓ -11,4%</td>
                <td class="val-positive">⇑ 7,7%</td>
              </tr>
              <tr>
                <td>Sessões</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
              </tr>
              <tr>
                <td>Tx. Conv.</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Combined Bar: SITE E APP -->
        <div class="combined-bar">
          <div class="combined-title">
            <span>SITE E APP</span>
            <span>Venda Efetiva: <strong>21.029 Mi</strong></span>
          </div>
          <div class="combined-metrics">
            <span>Meta: <strong>20,74 Mi</strong></span>
            <span>Meta Mês: <strong>40,44 Mi</strong></span>
            <span>Desvio %: <strong class="val-positive">+1,38%</strong></span>
            <span>Desvio Nº: <strong>+285,55 Mil</strong></span>
            <span>Evolução: <strong class="val-positive">⇑ 49,80%</strong></span>
            <span>Crescimento: <strong class="val-positive">⇑ 10,05%</strong></span>
          </div>
        </div>
      </div>
    </section>

    <!-- ====================================================================
         VISÃO 2: TENDÊNCIAS & DESVIOS DIÁRIOS
         ==================================================================== -->
    <section class="view-panel" id="view-desvios">
      <!-- Filtro de Canal -->
      <div class="filter-pills-bar">
        <span style="font-weight: 700; font-size: 13px; text-transform: uppercase;">Canal Selecionado:</span>
        <div class="pill-group" id="channelPillsV2">
          <button class="pill-btn" data-channel="canais_digitais">Canais Digitais (Total)</button>
          <button class="pill-btn" data-channel="app">App</button>
          <button class="pill-btn active" data-channel="marketplace">MKP</button>
          <button class="pill-btn" data-channel="site">Site</button>
          <button class="pill-btn" data-channel="figital">Figital</button>
        </div>
      </div>

      <!-- Gráfico 1: Ticket Médio Diário vs Meta -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>Ticket Médio Diário</h3>
          <div class="chart-legend-custom">
            <span class="legend-item"><span class="legend-dot" style="background: #0077ff;"></span> Ticket Médio Real</span>
            <span class="legend-item"><span class="legend-dot" style="background: #94a3b8;"></span> Meta Ticket Médio</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="chartTkm"></canvas>
        </div>
      </div>

      <!-- Gráfico 2: Desvio Rentabilidade Operacional Diária -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>Desvio Rent. Operacional (%)</h3>
          <div class="chart-legend-custom">
            <span class="legend-item"><span class="legend-dot" style="background: #0056b3;"></span> Rentabilidade %</span>
            <span class="legend-item"><span class="legend-dot" style="background: #38bdf8;"></span> Desvio % vs Meta</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="chartRent"></canvas>
        </div>
      </div>

      <!-- Gráfico 3: Desvio Faturamento Diário -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>Faturamento Diário & Desvio R$ (GAP)</h3>
          <div class="chart-legend-custom">
            <span class="legend-item"><span class="legend-dot" style="background: #cbd5e1;"></span> Faturamento Diário</span>
            <span class="legend-item"><span class="legend-dot" style="background: #0077ff;"></span> Desvio Faturamento R$</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="chartFat"></canvas>
        </div>
      </div>
    </section>

    <!-- ====================================================================
         VISÃO 3: TRÁFEGO, CONVERSÃO E ORIGENS
         ==================================================================== -->
    <section class="view-panel" id="view-trafego">
      <!-- Filtros de Canal e Origem -->
      <div class="filter-pills-bar">
        <div class="pill-group">
          <span style="font-weight: 700; font-size: 13px; text-transform: uppercase;">Canal:</span>
          <button class="pill-btn active" data-traffic-ch="app">App</button>
          <button class="pill-btn" data-traffic-ch="site">Site</button>
        </div>
        <span style="font-size: 11px; color: var(--text-muted); font-style: italic;">
          *Fonte integrada GA4 / Supermetrics com atualização matinal D-1.
        </span>
      </div>

      <!-- Gráfico 1: Taxa de Conversão Diária vs Meta -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>Taxa de Conversão Diária (%)</h3>
          <div class="chart-legend-custom">
            <span class="legend-item"><span class="legend-dot" style="background: #0077ff;"></span> Taxa de Conversão Real</span>
            <span class="legend-item"><span class="legend-dot" style="background: #003875;"></span> Meta Tx. Conv</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="chartConv"></canvas>
        </div>
      </div>

      <!-- Gráfico 2: Desvio de Sessões Diárias -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>Sessões Diárias & Desvio % vs Meta</h3>
          <div class="chart-legend-custom">
            <span class="legend-item"><span class="legend-dot" style="background: #cbd5e1;"></span> Sessões Realizadas</span>
            <span class="legend-item"><span class="legend-dot" style="background: #003875;"></span> Desvio Sessões %</span>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="chartSess"></canvas>
        </div>
      </div>

      <!-- Tabela de Origens de Tráfego / Canais de Mídia -->
      <div class="traffic-table-card">
        <h3>Desempenho por Origem de Tráfego / Canal de Mídia</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Origem / Mídia</th>
              <th>Canal</th>
              <th>Sessões</th>
              <th>Pedidos</th>
              <th>Tx. Conversão</th>
              <th>Receita (R$)</th>
              <th>Share</th>
            </tr>
          </thead>
          <tbody>
            {"".join([f'''<tr>
              <td>{o['origem']}</td>
              <td>{o['canal']}</td>
              <td>{o['sessoes']:,}</td>
              <td>{o['pedidos']:,}</td>
              <td>{o['tx_conv']*100:.2f}%</td>
              <td>R$ {o['receita']:,.2f}</td>
              <td>{o['share']*100:.1f}%</td>
            </tr>''' for o in origens])}
          </tbody>
        </table>
      </div>
    </section>

    <!-- ====================================================================
         VISÃO 4: PROJEÇÃO DE FECHAMENTO & SIMULADOR
         ==================================================================== -->
    <section class="view-panel" id="view-projecoes">
      <div class="top-header" style="padding: 16px 20px;">
        <div>
          <h3 style="font-family: 'Outfit'; font-size: 18px;">Simulador de Fechamento & Ritmo Diário Necessário</h3>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
            Cálculo estatístico do faturamento necessário por dia para alcançar 100% da meta de Setembro/2026 nos 15 dias restantes.
          </p>
        </div>
      </div>

      <div class="projection-grid">
        {"".join([f'''
        <div class="proj-card">
          <div class="proj-card-header">
            <h4 style="font-size: 16px; font-weight: 800; font-family: 'Outfit';">{ch.replace('_', ' ').upper()}</h4>
            <span class="hero-part-badge">Meta Mês: R$ {p['meta_mes']/1e6:.3f} Mi</span>
          </div>
          <div class="proj-metrics-row">
            <div class="proj-box">
              <div class="lbl">Realizado (15 Dias)</div>
              <div class="val">R$ {p['venda_realizada']/1e6:.3f} Mi</div>
            </div>
            <div class="proj-box">
              <div class="lbl">Meta Restante</div>
              <div class="val">R$ {p['meta_restante']/1e6:.3f} Mi</div>
            </div>
            <div class="proj-box">
              <div class="lbl">Meta Diária Necessária</div>
              <div class="val" style="color: var(--fsj-blue-light);">R$ {p['venda_diaria_necessaria']/1e3:,.0f} K/dia</div>
            </div>
          </div>
          <div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 4px;">
              <span>Fechamento Projetado: <strong>R$ {p['fechamento_projetado']/1e6:.3f} Mi</strong></span>
              <span class="{'val-positive' if p['atingimento_projetado_pct'] >= 100 else 'val-negative'}">
                {p['atingimento_projetado_pct']:.1f}% da Meta
              </span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" style="width: {min(100, p['atingimento_projetado_pct'])}%;"></div>
            </div>
          </div>
        </div>
        ''' for ch, p in proj.items() if ch in ['ecommerce_total', 'canais_digitais', 'app', 'site', 'marketplace', 'figital']])}
      </div>
    </section>
  </main>

  <!-- JAVASCRIPT LOGIC -->
  <script>
    const dashData = {json.dumps(dash_data)};
    console.log("Dados carregados:", dashData);

    // Navegação entre Visões
    const navBtns = document.querySelectorAll('.nav-btn');
    const viewPanels = document.querySelectorAll('.view-panel');

    navBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const targetViewId = btn.getAttribute('data-view');
        viewPanels.forEach(p => {{
          if (p.id === targetViewId) {{
            p.classList.add('active');
          }} else {{
            p.classList.remove('active');
          }}
        }});

        if (targetViewId === 'view-desvios') {{
          renderDesviosCharts(currentChannelV2);
        }} else if (targetViewId === 'view-trafego') {{
          renderTrafficCharts(currentTrafficCh);
        }}
      }});
    }});

    // Alternância Modo Escuro / Claro
    const themeBtn = document.getElementById('themeBtn');
    let currentTheme = localStorage.getItem('fsj_theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeBtn.addEventListener('click', () => {{
      currentTheme = currentTheme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', currentTheme);
      localStorage.setItem('fsj_theme', currentTheme);
      if (chartTkmInstance) renderDesviosCharts(currentChannelV2);
      if (chartConvInstance) renderTrafficCharts(currentTrafficCh);
    }});

    // Registra plugin de rótulos nos gráficos
    if (typeof ChartDataLabels !== 'undefined') {{
      Chart.register(ChartDataLabels);
    }}

    // =========================================================================
    // RENDERIZADOR DE GRÁFICOS — VISÃO 2 (TENDÊNCIAS & DESVIOS)
    // =========================================================================
    let currentChannelV2 = 'marketplace';
    let chartTkmInstance = null;
    let chartRentInstance = null;
    let chartFatInstance = null;

    const pillBtnsV2 = document.querySelectorAll('#channelPillsV2 .pill-btn');
    pillBtnsV2.forEach(btn => {{
      btn.addEventListener('click', () => {{
        pillBtnsV2.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentChannelV2 = btn.getAttribute('data-channel');
        renderDesviosCharts(currentChannelV2);
      }});
    }});

    function getGridColor() {{
      return currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)';
    }}

    function getTextColor() {{
      return currentTheme === 'dark' ? '#94a3b8' : '#64748b';
    }}

    function renderDesviosCharts(channelKey) {{
      const cData = dashData.charts[channelKey] || dashData.charts['marketplace'];
      const labels = dashData.charts.labels;

      // 1. Chart Ticket Médio
      if (chartTkmInstance) chartTkmInstance.destroy();
      const ctxTkm = document.getElementById('chartTkm').getContext('2d');
      chartTkmInstance = new Chart(ctxTkm, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Ticket Médio Real',
              data: cData.tkm.real,
              borderColor: '#0077ff',
              backgroundColor: 'rgba(0, 119, 255, 0.08)',
              borderWidth: 2.8,
              fill: true,
              tension: 0.25,
              pointBackgroundColor: cData.tkm.real.map((v, i) => v >= cData.tkm.meta[i] ? '#0077ff' : '#ef4444'),
              pointBorderColor: '#ffffff',
              pointRadius: 5.5,
              pointHoverRadius: 8,
              datalabels: {{
                display: true,
                align: 'top',
                anchor: 'end',
                offset: 5,
                font: {{ size: 10, weight: '700' }},
                color: ctx => ctx.dataset.data[ctx.dataIndex] >= cData.tkm.meta[ctx.dataIndex] ? (currentTheme === 'dark' ? '#38bdf8' : '#0056b3') : '#ef4444',
                formatter: val => val.toFixed(2).replace('.', ',')
              }}
            }},
            {{
              label: 'Meta Ticket Médio',
              data: cData.tkm.meta,
              borderColor: '#94a3b8',
              borderWidth: 2,
              borderDash: [5, 5],
              fill: false,
              pointRadius: 0,
              datalabels: {{ display: false }}
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 25, bottom: 12, left: 16, right: 16 }} }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: R$ ${{ctx.raw.toFixed(2)}}`
              }}
            }}
          }},
          scales: {{
            y: {{
              grid: {{ color: getGridColor() }},
              ticks: {{ color: getTextColor() }}
            }},
            x: {{
              offset: true,
              grid: {{ display: false }},
              ticks: {{ color: getTextColor() }}
            }}
          }}
        }}
      }});

      // 2. Chart Rentabilidade Operacional (Eixo Duplo Harmonizado)
      if (chartRentInstance) chartRentInstance.destroy();
      const ctxRent = document.getElementById('chartRent').getContext('2d');
      chartRentInstance = new Chart(ctxRent, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Rentabilidade %',
              data: cData.rent_op.real,
              borderColor: '#003875',
              backgroundColor: 'transparent',
              borderWidth: 2.6,
              tension: 0.25,
              pointRadius: 4.5,
              yAxisID: 'y',
              datalabels: {{
                display: true,
                align: 'top',
                offset: 6,
                font: {{ size: 10, weight: '700' }},
                color: () => currentTheme === 'dark' ? '#f8fafc' : '#003875',
                formatter: val => val.toFixed(1).replace('.', ',') + '%'
              }}
            }},
            {{
              label: 'Desvio % vs Meta',
              data: cData.rent_op.desvio,
              borderColor: '#0077ff',
              backgroundColor: 'transparent',
              borderWidth: 2.2,
              tension: 0.25,
              pointRadius: 4.5,
              yAxisID: 'y1',
              datalabels: {{
                display: true,
                align: 'bottom',
                offset: 6,
                borderRadius: 4,
                padding: {{ top: 2, bottom: 2, left: 4, right: 4 }},
                backgroundColor: ctx => ctx.dataset.data[ctx.dataIndex] >= 0 ? (currentTheme === 'dark' ? 'rgba(34,197,94,0.2)' : '#dcfce7') : (currentTheme === 'dark' ? 'rgba(239,68,68,0.2)' : '#fee2e2'),
                font: {{ size: 9.5, weight: '800' }},
                color: ctx => ctx.dataset.data[ctx.dataIndex] >= 0 ? '#16a34a' : '#dc2626',
                formatter: val => (val > 0 ? '+' : '') + val.toFixed(1).replace('.', ',') + '%'
              }}
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 25, bottom: 15, left: 16, right: 16 }} }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: ${{ctx.raw.toFixed(1)}}%`
              }}
            }}
          }},
          scales: {{
            y: {{
              position: 'left',
              grid: {{ color: getGridColor() }},
              suggestedMin: -15,
              suggestedMax: 38,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return val + '%'; }}
              }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
              suggestedMin: -15,
              suggestedMax: 38,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return val + '%'; }}
              }}
            }},
            x: {{
              offset: true,
              grid: {{ display: false }},
              ticks: {{ color: getTextColor() }}
            }}
          }}
        }}
      }});

      // 3. Chart Faturamento & Desvio GAP (Eixo Harmonizado - Sem Sobreposição)
      if (chartFatInstance) chartFatInstance.destroy();
      const ctxFat = document.getElementById('chartFat').getContext('2d');
      chartFatInstance = new Chart(ctxFat, {{
        data: {{
          labels: labels,
          datasets: [
            {{
              type: 'bar',
              label: 'Faturamento Real',
              data: cData.faturamento.real,
              backgroundColor: currentTheme === 'dark' ? '#334155' : '#cbd5e1',
              borderRadius: 6,
              yAxisID: 'y',
              order: 2,
              datalabels: {{
                display: true,
                anchor: 'end',
                align: 'top',
                offset: 4,
                font: {{ size: 10, weight: '700' }},
                color: () => currentTheme === 'dark' ? '#f8fafc' : '#1e293b',
                formatter: val => Math.round(val / 1000) + ' K'
              }}
            }},
            {{
              type: 'line',
              label: 'Desvio Faturamento R$',
              data: cData.faturamento.desvio,
              borderColor: '#0077ff',
              borderWidth: 2.8,
              tension: 0.2,
              pointRadius: 5,
              pointBackgroundColor: '#0077ff',
              yAxisID: 'y1',
              order: 1,
              datalabels: {{
                display: true,
                align: 'top',
                offset: 6,
                borderRadius: 4,
                padding: {{ top: 2, bottom: 2, left: 5, right: 5 }},
                backgroundColor: ctx => ctx.dataset.data[ctx.dataIndex] >= 0 ? '#0077ff' : '#dc2626',
                font: {{ size: 9.5, weight: '800' }},
                color: '#ffffff',
                formatter: val => (val > 0 ? '+' : '') + Math.round(val / 1000) + 'K'
              }}
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 28, bottom: 12, left: 16, right: 16 }} }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: R$ ${{ctx.raw.toLocaleString('pt-BR')}}`
              }}
            }}
          }},
          scales: {{
            y: {{
              position: 'left',
              grid: {{ color: getGridColor() }},
              suggestedMin: -50000,
              suggestedMax: 820000,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return 'R$ ' + (val/1000).toFixed(0) + 'K'; }}
              }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
              suggestedMin: -50000,
              suggestedMax: 820000,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return (val/1000).toFixed(0) + 'K'; }}
              }}
            }},
            x: {{
              offset: true,
              grid: {{ display: false }},
              ticks: {{ color: getTextColor() }}
            }}
          }}
        }}
      }});
    }}

    // =========================================================================
    // RENDERIZADOR DE GRÁFICOS — VISÃO 3 (TRÁFEGO & CONVERSÃO)
    // =========================================================================
    let currentTrafficCh = 'app';
    let chartConvInstance = null;
    let chartSessInstance = null;

    const trafficPillBtns = document.querySelectorAll('[data-traffic-ch]');
    trafficPillBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        trafficPillBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentTrafficCh = btn.getAttribute('data-traffic-ch');
        renderTrafficCharts(currentTrafficCh);
      }});
    }});

    function renderTrafficCharts(channelKey) {{
      const cData = dashData.charts[channelKey] || dashData.charts['app'];
      const labels = dashData.charts.labels;

      // 1. Chart Conversão
      if (chartConvInstance) chartConvInstance.destroy();
      const ctxConv = document.getElementById('chartConv').getContext('2d');
      chartConvInstance = new Chart(ctxConv, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Taxa de Conversão Real',
              data: cData.tx_conv ? cData.tx_conv.real : [],
              borderColor: '#0077ff',
              backgroundColor: 'rgba(0, 119, 255, 0.08)',
              borderWidth: 2.8,
              fill: true,
              tension: 0.25,
              pointRadius: 5.5,
              datalabels: {{
                display: true,
                align: 'top',
                offset: 5,
                font: {{ size: 10, weight: '700' }},
                color: () => currentTheme === 'dark' ? '#38bdf8' : '#0077ff',
                formatter: val => val.toFixed(1).replace('.', ',') + '%'
              }}
            }},
            {{
              label: 'Meta Tx. Conv',
              data: cData.tx_conv ? cData.tx_conv.meta : [],
              borderColor: '#003875',
              borderWidth: 2,
              borderDash: [5, 5],
              fill: false,
              pointRadius: 0,
              datalabels: {{ display: false }}
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 25, bottom: 12, left: 16, right: 16 }} }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: ${{ctx.raw.toFixed(2)}}%`
              }}
            }}
          }},
          scales: {{
            y: {{
              grid: {{ color: getGridColor() }},
              suggestedMin: channelKey === 'site' ? 1 : 7,
              suggestedMax: channelKey === 'site' ? 4.5 : 18,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return val + '%'; }}
              }}
            }},
            x: {{
              offset: true,
              grid: {{ display: false }},
              ticks: {{ color: getTextColor() }}
            }}
          }}
        }}
      }});

      // 2. Chart Sessões (Eixo Duplo com Separação de Zonas)
      if (chartSessInstance) chartSessInstance.destroy();
      const ctxSess = document.getElementById('chartSess').getContext('2d');
      chartSessInstance = new Chart(ctxSess, {{
        data: {{
          labels: labels,
          datasets: [
            {{
              type: 'bar',
              label: 'Sessões Realizadas',
              data: cData.sessoes ? cData.sessoes.real : [],
              backgroundColor: currentTheme === 'dark' ? '#334155' : '#cbd5e1',
              borderRadius: 6,
              yAxisID: 'y',
              order: 2,
              datalabels: {{
                display: true,
                anchor: 'end',
                align: 'top',
                offset: 4,
                font: {{ size: 10, weight: '700' }},
                color: () => currentTheme === 'dark' ? '#f8fafc' : '#1e293b',
                formatter: val => val.toLocaleString('pt-BR')
              }}
            }},
            {{
              type: 'line',
              label: 'Desvio Sessões %',
              data: cData.sessoes ? cData.sessoes.desvio : [],
              borderColor: '#003875',
              borderWidth: 2.8,
              tension: 0.2,
              pointRadius: 5,
              yAxisID: 'y1',
              order: 1,
              datalabels: {{
                display: true,
                align: 'top',
                offset: 5,
                borderRadius: 4,
                padding: {{ top: 2, bottom: 2, left: 4, right: 4 }},
                backgroundColor: ctx => ctx.dataset.data[ctx.dataIndex] >= 0 ? '#16a34a' : '#dc2626',
                font: {{ size: 9.5, weight: '800' }},
                color: '#ffffff',
                formatter: val => (val > 0 ? '+' : '') + val + '%'
              }}
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 28, bottom: 12, left: 16, right: 16 }} }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: ${{ctx.raw.toLocaleString('pt-BR')}}`
              }}
            }}
          }},
          scales: {{
            y: {{
              position: 'left',
              grid: {{ color: getGridColor() }},
              min: 0,
              max: channelKey === 'site' ? 120000 : 100000,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return (val/1000).toFixed(0) + ' Mil'; }}
              }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
              min: channelKey === 'site' ? -45 : -25,
              max: channelKey === 'site' ? 25 : 65,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return val + '%'; }}
              }}
            }},
            x: {{
              offset: true,
              grid: {{ display: false }},
              ticks: {{ color: getTextColor() }}
            }}
          }}
        }}
      }});
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Dashboard compilado com sucesso em {time.time() - t0:.2f}s!")
    print(f"Arquivo gerado: {OUTPUT_HTML}")
    return OUTPUT_HTML

if __name__ == '__main__':
    build()
