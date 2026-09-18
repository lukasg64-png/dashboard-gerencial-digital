"""
build_dashboard_gerencial.py — Compilador do Dashboard Gerencial Digital & Figital.
Gera a aplicação web executiva completa 'index.html' autônoma, responsiva e ultra-veloz.
Design System: Apple Human Interface + Identidade Visual Farmácias São João.
Recursos:
- Filtro Interativo de Período (MTD, Ontem D-1, Últimos 7 Dias, Histórico Diário com seletor de dia a dia)
- Toggle de Figital (Somar Figital aos Totais de Canais Digitais e E-Commerce)
- Gráficos Chart.js 4 interativos com DataLabels
- Projeção de Fechamento de Mês e Run Rate
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

def fmt_curr(val):
    if abs(val) >= 1e6:
        return f"R$ {val/1e6:.3f} Mi"
    elif abs(val) >= 1e3:
        return f"R$ {val/1e3:,.1f} K"
    return f"R$ {val:,.2f}"

def fmt_gap(val):
    sign = "+" if val >= 0 else ""
    if abs(val) >= 1e6:
        return f"{sign}{val/1e6:.3f} Mi"
    elif abs(val) >= 1e3:
        return f"{sign}{val/1e3:,.1f} K"
    return f"{sign}{val:,.2f}"

def fmt_pct(val):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%"

def fmt_growth(val):
    if val >= 0:
        return f"⇑ {val:.1f}%"
    return f"⇓ {abs(val):.1f}%"

def render_channel_table_rows(ch_key, k):
    m = k[ch_key]
    rows = []
    
    # 1. Venda
    v_real_str = f"{m['venda']/1e6:.3f} Mi" if m['venda'] >= 1e6 else f"{m['venda']/1e3:.1f} K"
    v_meta_str = f"{m['meta_mtd']/1e6:.3f} Mi" if m['meta_mtd'] >= 1e6 else f"{m['meta_mtd']/1e3:.1f} K"
    v_mes_str = f"{m['meta_mes']/1e6:.3f} Mi" if m['meta_mes'] >= 1e6 else f"{m['meta_mes']/1e3:.1f} K"
    v_desv_cls = 'val-positive' if m['desvio_venda_pct'] >= 0 else 'val-negative'
    v_desv_str = fmt_pct(m['desvio_venda_pct'])
    v_evo_cls = 'val-positive' if m['evo_yoy'] >= 0 else 'val-negative'
    v_evo_str = fmt_growth(m['evo_yoy'])
    v_cresc_cls = 'val-positive' if m['cresc_mom'] >= 0 else 'val-negative'
    v_cresc_str = fmt_growth(m['cresc_mom'])

    rows.append(f'''<tr id="row-{ch_key}-venda">
      <td>Venda</td>
      <td id="{ch_key}-venda-real">{v_real_str}</td>
      <td id="{ch_key}-venda-meta">{v_meta_str}</td>
      <td id="{ch_key}-venda-mes">{v_mes_str}</td>
      <td id="{ch_key}-venda-desv" class="{v_desv_cls}">{v_desv_str}</td>
      <td id="{ch_key}-venda-evo" class="{v_evo_cls}">{v_evo_str}</td>
      <td id="{ch_key}-venda-cresc" class="{v_cresc_cls}">{v_cresc_str}</td>
    </tr>''')

    # 2. Qtd NF / Cupons
    c_real_str = f"{m['cupons']/1e3:,.2f} Mil" if m['cupons'] >= 1e3 else f"{m['cupons']}"
    c_meta_str = f"{m['cupons_meta_mtd']/1e3:,.2f} Mil" if m['cupons_meta_mtd'] >= 1e3 else f"{m['cupons_meta_mtd']}"
    c_mes_val = m.get('cupons_meta_mes', m['cupons_meta_mtd'] * 2)
    c_mes_str = f"{c_mes_val/1e3:,.2f} Mil" if c_mes_val >= 1e3 else f"{c_mes_val}"
    c_desv_cls = 'val-positive' if m['cupons_desvio_pct'] >= 0 else 'val-negative'
    c_desv_str = fmt_pct(m['cupons_desvio_pct'])
    rows.append(f'''<tr id="row-{ch_key}-cupons">
      <td>Qtd. NF</td>
      <td id="{ch_key}-cupons-real">{c_real_str}</td>
      <td id="{ch_key}-cupons-meta">{c_meta_str}</td>
      <td id="{ch_key}-cupons-mes">{c_mes_str}</td>
      <td id="{ch_key}-cupons-desv" class="{c_desv_cls}">{c_desv_str}</td>
      <td id="{ch_key}-cupons-evo" class="{v_evo_cls}">{v_evo_str}</td>
      <td id="{ch_key}-cupons-cresc" class="{v_cresc_cls}">{v_cresc_str}</td>
    </tr>''')

    # 3. Ticket Médio
    t_real_str = f"{m['tkm']:.2f}".replace('.', ',')
    t_meta_str = f"{m['tkm_meta']:.2f}".replace('.', ',')
    t_desv_cls = 'val-positive' if m['tkm_desvio_pct'] >= 0 else 'val-negative'
    t_desv_str = fmt_pct(m['tkm_desvio_pct'])
    rows.append(f'''<tr id="row-{ch_key}-tkm">
      <td>Ticket M.</td>
      <td id="{ch_key}-tkm-real">{t_real_str}</td>
      <td id="{ch_key}-tkm-meta">{t_meta_str}</td>
      <td id="{ch_key}-tkm-mes">{t_meta_str}</td>
      <td id="{ch_key}-tkm-desv" class="{t_desv_cls}">{t_desv_str}</td>
      <td id="{ch_key}-tkm-evo" class="{t_desv_cls}">{"⇑" if m['tkm_desvio_pct']>=0 else "⇓"} {abs(m['tkm_desvio_pct']):.1f}%</td>
      <td id="{ch_key}-tkm-cresc" class="{t_desv_cls}">{"⇑" if m['tkm_desvio_pct']>=0 else "⇓"} {abs(m['tkm_desvio_pct']):.1f}%</td>
    </tr>''')

    # 4. Rentabilidade Operacional
    r_real_str = f"{m['rent_op']:.2f}%".replace('.', ',')
    r_meta_str = f"{m['rent_op_meta']:.2f}%".replace('.', ',')
    r_desv_cls = 'val-positive' if m['rent_op_desvio'] >= 0 else 'val-negative'
    r_desv_str = fmt_pct(m['rent_op_desvio'])
    rows.append(f'''<tr id="row-{ch_key}-rent">
      <td>Rent. Op.</td>
      <td id="{ch_key}-rent-real">{r_real_str}</td>
      <td id="{ch_key}-rent-meta">{r_meta_str}</td>
      <td id="{ch_key}-rent-mes">{r_meta_str}</td>
      <td id="{ch_key}-rent-desv" class="{r_desv_cls}">{r_desv_str}</td>
      <td id="{ch_key}-rent-evo" class="{r_desv_cls}">{"⇑" if m['rent_op_desvio']>=0 else "⇓"} {abs(m['rent_op_desvio']):.1f}%</td>
      <td id="{ch_key}-rent-cresc" class="{r_desv_cls}">{"⇑" if m['rent_op_desvio']>=0 else "⇓"} {abs(m['rent_op_desvio']):.1f}%</td>
    </tr>''')

    # 5 & 6. Sessões e Taxa Conv (para App e Site)
    if ch_key in ['app', 'site']:
        s_real_str = f"{m['sessoes']/1e6:.2f} Mi" if m['sessoes'] >= 1e6 else f"{m['sessoes']/1e3:,.0f} K"
        s_meta_str = f"{m['sessoes_meta_mtd']/1e6:.2f} Mi" if m['sessoes_meta_mtd'] >= 1e6 else f"{m['sessoes_meta_mtd']/1e3:,.0f} K"
        s_mes_val = m.get('sessoes_meta_mes', m['sessoes_meta_mtd'] * 2)
        s_mes_str = f"{s_mes_val/1e6:.2f} Mi" if s_mes_val >= 1e6 else f"{s_mes_val/1e3:,.0f} K"
        s_desv_cls = 'val-positive' if m['sessoes_desvio_pct'] >= 0 else 'val-negative'
        s_desv_str = fmt_pct(m['sessoes_desvio_pct'])
        rows.append(f'''<tr id="row-{ch_key}-sess">
          <td>Sessões</td>
          <td id="{ch_key}-sess-real">{s_real_str}</td>
          <td id="{ch_key}-sess-meta">{s_meta_str}</td>
          <td id="{ch_key}-sess-mes">{s_mes_str}</td>
          <td id="{ch_key}-sess-desv" class="{s_desv_cls}">{s_desv_str}</td>
          <td id="{ch_key}-sess-evo" class="{s_desv_cls}">{"⇑" if m['sessoes_desvio_pct']>=0 else "⇓"} {abs(m['sessoes_desvio_pct']):.1f}%</td>
          <td id="{ch_key}-sess-cresc" class="{s_desv_cls}">{"⇑" if m['sessoes_desvio_pct']>=0 else "⇓"} {abs(m['sessoes_desvio_pct']):.1f}%</td>
        </tr>''')

        tx_real_str = f"{m['tx_conv']:.2f}%".replace('.', ',')
        tx_meta_str = f"{m['tx_conv_meta']:.2f}%".replace('.', ',')
        tx_desv_cls = 'val-positive' if m['tx_conv_desvio_pct'] >= 0 else 'val-negative'
        tx_desv_str = fmt_pct(m['tx_conv_desvio_pct'])
        rows.append(f'''<tr id="row-{ch_key}-tx">
          <td>Tx. Conv.</td>
          <td id="{ch_key}-tx-real">{tx_real_str}</td>
          <td id="{ch_key}-tx-meta">{tx_meta_str}</td>
          <td id="{ch_key}-tx-mes">{tx_meta_str}</td>
          <td id="{ch_key}-tx-desv" class="{tx_desv_cls}">{tx_desv_str}</td>
          <td id="{ch_key}-tx-evo" class="{tx_desv_cls}">{"⇑" if m['tx_conv_desvio_pct']>=0 else "⇓"} {abs(m['tx_conv_desvio_pct']):.1f}%</td>
          <td id="{ch_key}-tx-cresc" class="{tx_desv_cls}">{"⇑" if m['tx_conv_desvio_pct']>=0 else "⇓"} {abs(m['tx_conv_desvio_pct']):.1f}%</td>
        </tr>''')
    else:
        rows.append(f'''<tr id="row-{ch_key}-sess">
          <td>Sessões</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
        </tr>''')
        rows.append(f'''<tr id="row-{ch_key}-tx">
          <td>Tx. Conv.</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
        </tr>''')

    return "\n".join(rows)

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
    max_dia = int(dash_data.get('max_dia', 17))
    dias_restantes = 30 - max_dia
    data_corte = dash_data.get('data_corte', f'01 a {max_dia:02d}/09/2026')
    atualizacao = dash_data.get('atualizacao', time.strftime('%Y-%m-%d %H:%M:%S'))

    # Pré-geração dos cards da Visão 4 com IDs para atualização dinâmica do Figital e Período
    proj_cards_list = []
    for ch in ['ecommerce_total', 'canais_digitais', 'app', 'site', 'marketplace', 'figital']:
        if ch in proj:
            p = proj[ch]
            ch_title = ch.replace('_', ' ').upper()
            fig_badge = f'<span class="badge-figital-pill" id="proj-{ch}-figital-badge" style="display: none;">+ Figital</span>' if ch in ['ecommerce_total', 'canais_digitais'] else ''
            val_pos_class = 'val-positive' if p['atingimento_projetado_pct'] >= 100 else 'val-negative'
            card_html = f'''
        <div class="proj-card" id="proj-card-{ch}">
          <div class="proj-card-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <h4 style="font-size: 16px; font-weight: 800; font-family: \'Outfit\';">{ch_title}</h4>
              {fig_badge}
            </div>
            <span class="hero-part-badge" id="proj-metames-{ch}">Meta Mês: R$ {p['meta_mes']/1e6:.3f} Mi</span>
          </div>
          <div class="proj-metrics-row">
            <div class="proj-box">
              <div class="lbl" id="proj-lbl-real-{ch}">Realizado ({max_dia} Dias)</div>
              <div class="val" id="proj-real-{ch}">R$ {p['venda_realizada']/1e6:.3f} Mi</div>
            </div>
            <div class="proj-box">
              <div class="lbl">Meta Restante</div>
              <div class="val" id="proj-restante-{ch}">R$ {p['meta_restante']/1e6:.3f} Mi</div>
            </div>
            <div class="proj-box">
              <div class="lbl">Meta Diária Necessária</div>
              <div class="val" id="proj-diaria-{ch}" style="color: var(--fsj-blue-light);">R$ {p['venda_diaria_necessaria']/1e3:,.0f} K/dia</div>
            </div>
          </div>
          <div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 4px;">
              <span>Fechamento Projetado: <strong id="proj-fechamento-{ch}">R$ {p['fechamento_projetado']/1e6:.3f} Mi</strong></span>
              <span class="{val_pos_class}" id="proj-ating-{ch}">
                {p['atingimento_projetado_pct']:.1f}% da Meta
              </span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" id="proj-progress-{ch}" style="width: {min(100, p['atingimento_projetado_pct'])}%;"></div>
            </div>
          </div>
        </div>'''
            proj_cards_list.append(card_html)
    proj_cards_html = "".join(proj_cards_list)

    # Opções do Seletor de Histórico Diário
    day_options_html = "".join([f'<option value="{d}">Dia {d:02d}/09</option>' for d in range(max_dia, 0, -1)])

    # Tabelas de canais
    site_table_rows = render_channel_table_rows('site', kpis)
    app_table_rows = render_channel_table_rows('app', kpis)
    mkp_table_rows = render_channel_table_rows('marketplace', kpis)

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
      transition: var(--transition);
      position: relative;
    }}

    .nav-btn svg {{
      width: 24px;
      height: 24px;
      stroke-width: 2;
      transition: var(--transition);
    }}

    .nav-btn:hover {{
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
      transform: scale(1.05);
    }}

    .nav-btn.active {{
      background: #ffffff;
      color: var(--fsj-blue);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      transform: scale(1.05);
    }}

    .nav-btn.active svg {{
      stroke-width: 2.5;
    }}

    .sidebar-spacer {{
      flex: 1;
    }}

    /* ==========================================================================
       LAYOUT PRINCIPAL & CABEÇALHO EXECUTIVO
       ========================================================================== */
    .main-wrapper {{
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 24px 32px 60px 32px;
      max-width: 1720px;
      margin: 0 auto;
      width: calc(100% - 78px);
    }}

    .top-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-card);
    }}

    .header-titles h1 {{
      font-size: 24px;
      font-weight: 800;
      color: var(--text-primary);
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .header-titles p {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-top: 4px;
      font-weight: 500;
    }}

    .tag-figital {{
      font-size: 11px;
      background: linear-gradient(135deg, #8b5cf6, #3b82f6);
      color: white;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25);
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .period-control-group {{
      display: flex;
      align-items: center;
      gap: 8px;
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
      box-shadow: var(--shadow-sm);
    }}

    .period-select-box svg {{
      color: var(--fsj-blue-light);
    }}

    .period-select {{
      border: none;
      background: transparent;
      color: inherit;
      font-size: 13px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    .day-select-box {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      padding: 6px 12px;
      border-radius: var(--radius-pill);
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      animation: fadeIn 0.25s ease;
      box-shadow: var(--shadow-sm);
    }}

    .day-select-label {{
      font-size: 11px;
      font-weight: 800;
      color: var(--fsj-blue-light);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .day-select {{
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-size: 13px;
      font-weight: 700;
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
      box-shadow: var(--shadow-sm);
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

    /* SWITCH BAR EM CIMA NO BLOCO DO FIGITAL */
    .figital-switch-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      padding: 7px 10px;
      margin-bottom: 4px;
      transition: var(--transition);
      cursor: pointer;
      user-select: none;
    }}

    .figital-switch-bar:hover {{
      border-color: #8b5cf6;
      background: rgba(139, 92, 246, 0.06);
    }}

    .figital-switch-bar.active-on {{
      border-color: rgba(139, 92, 246, 0.6);
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(59, 130, 246, 0.08));
      box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
    }}

    .figital-switch-info {{
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    .switch-pulse-indicator {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #94a3b8;
      transition: var(--transition);
    }}

    .figital-switch-bar.active-on .switch-pulse-indicator {{
      background: #22c55e;
      box-shadow: 0 0 8px #22c55e;
      animation: pulseGreen 2s infinite;
    }}

    @keyframes pulseGreen {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.6; transform: scale(1.2); }}
    }}

    .switch-text-group {{
      display: flex;
      flex-direction: column;
      line-height: 1.15;
    }}

    .switch-title-text {{
      font-size: 11.5px;
      font-weight: 700;
      letter-spacing: 0.2px;
      color: var(--text-primary);
    }}

    .switch-desc-text {{
      font-size: 10px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .figital-switch-action {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .switch-mode-tag {{
      font-size: 9.5px;
      font-weight: 800;
      letter-spacing: 0.5px;
      padding: 2px 5px;
      border-radius: var(--radius-sm);
      background: var(--border-card);
      color: var(--text-secondary);
      transition: var(--transition);
    }}

    .figital-switch-bar.active-on .switch-mode-tag {{
      background: #8b5cf6;
      color: #ffffff;
    }}

    /* Apple Switch Element */
    .apple-switch {{
      position: relative;
      display: inline-block;
      width: 38px;
      height: 22px;
    }}

    .apple-switch input {{
      opacity: 0;
      width: 0;
      height: 0;
    }}

    .apple-slider {{
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #cbd5e1;
      transition: .3s;
      border-radius: 22px;
    }}

    [data-theme="dark"] .apple-slider {{
      background-color: #334155;
    }}

    .apple-slider:before {{
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .3s;
      border-radius: 50%;
      box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }}

    input:checked + .apple-slider {{
      background-color: #8b5cf6;
    }}

    input:checked + .apple-slider:before {{
      transform: translateX(16px);
    }}

    .hero-card.figital-integrated {{
      border-color: rgba(139, 92, 246, 0.4);
      box-shadow: 0 4px 15px rgba(139, 92, 246, 0.12);
    }}

    .badge-figital-pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10px;
      font-weight: 700;
      background: rgba(139, 92, 246, 0.15);
      color: #8b5cf6;
      padding: 2px 6px;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(139, 92, 246, 0.3);
      animation: fadeIn 0.2s ease;
    }}

    .hero-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .hero-title-group h3 {{
      font-size: 16px;
      font-weight: 800;
      letter-spacing: -0.2px;
      font-family: 'Outfit', sans-serif;
    }}

    .hero-subtitle {{
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .hero-part-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      background: var(--badge-blue-bg);
      color: var(--badge-blue-text);
    }}

    .hero-val-group {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}

    .hero-main-val {{
      font-size: 26px;
      font-weight: 800;
      font-family: 'Outfit', sans-serif;
      color: var(--text-primary);
      letter-spacing: -0.5px;
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

    /* Barra Combinada Site e App */
    .combined-bar {{
      grid-column: 1 / -1;
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow-sm);
    }}

    .combined-title {{
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 14px;
      font-weight: 700;
    }}

    .combined-metrics {{
      display: flex;
      align-items: center;
      gap: 20px;
      font-size: 13px;
      color: var(--text-secondary);
    }}

    .combined-metrics span strong {{
      color: var(--text-primary);
      font-weight: 700;
    }}

    /* ==========================================================================
       VISÃO 2 & 3: GRÁFICOS & TABELAS
       ========================================================================== */
    .filter-pills-bar {{
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--bg-card);
      padding: 12px 18px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-card);
      box-shadow: var(--shadow-sm);
    }}

    .pill-group {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .pill-btn {{
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      cursor: pointer;
      transition: var(--transition);
    }}

    .pill-btn:hover {{
      background: var(--bg-card-hover);
      color: var(--fsj-blue);
      border-color: var(--fsj-blue-light);
    }}

    .pill-btn.active {{
      background: var(--fsj-blue);
      color: white;
      border-color: var(--fsj-blue);
      box-shadow: 0 2px 8px rgba(0, 86, 179, 0.25);
    }}

    .chart-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 22px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 14px;
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
    }}

    .chart-legend-custom {{
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 600;
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
      height: 310px;
      position: relative;
    }}

    .traffic-table-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 22px;
      box-shadow: var(--shadow-sm);
    }}

    .traffic-table-card h3 {{
      font-size: 16px;
      font-weight: 800;
      font-family: 'Outfit', sans-serif;
      margin-bottom: 16px;
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}

    .data-table th {{
      text-align: left;
      padding: 10px 12px;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border-card);
      font-weight: 700;
    }}

    .data-table td {{
      padding: 12px;
      border-bottom: 1px solid var(--border-card);
      color: var(--text-primary);
      font-weight: 600;
    }}

    .data-table tr:hover td {{
      background: var(--bg-card-subtle);
    }}

    /* ==========================================================================
       VISÃO 4: PROJEÇÃO DE FECHAMENTO
       ========================================================================== */
    .projection-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
    }}

    @media (max-width: 1200px) {{
      .projection-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .proj-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .proj-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-card);
      padding-bottom: 10px;
    }}

    .proj-metrics-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      text-align: center;
    }}

    .proj-box {{
      background: var(--bg-card-subtle);
      padding: 10px;
      border-radius: var(--radius-md);
    }}

    .proj-box .lbl {{
      font-size: 11px;
      color: var(--text-secondary);
      font-weight: 600;
      margin-bottom: 4px;
    }}

    .proj-box .val {{
      font-size: 14px;
      font-weight: 800;
      color: var(--text-primary);
    }}

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
        <!-- CONTROLES DE FILTRO DE DATA & HISTÓRICO -->
        <div class="period-control-group">
          <div class="period-select-box">
            <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <select class="period-select" id="periodFilter" title="Filtrar Período de Análise">
              <option value="mtd" selected>Acumulado MTD (01 a {max_dia:02d}/09)</option>
              <option value="d1">Ontem / D-1 ({max_dia:02d}/09 - Fechamento)</option>
              <option value="last7">Últimos 7 Dias ({max(1, max_dia-6):02d} a {max_dia:02d}/09)</option>
              <option value="day">Histórico Diário (Selecionar Dia)</option>
            </select>
          </div>

          <!-- SELETOR DE DIA INDIVIDUAL DO HISTÓRICO -->
          <div class="day-select-box" id="daySelectBox" style="display: none;">
            <span class="day-select-label">Dia:</span>
            <select class="day-select" id="dayHistorySelect" title="Selecione o Dia do Histórico">
              {day_options_html}
            </select>
          </div>
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
        <div class="hero-card highlight-card" id="cardEcommerce">
          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3>E-Commerce</h3>
                <span class="badge-figital-pill" id="ecomFigitalBadge" style="display: none;">+ Figital</span>
              </div>
              <span class="hero-subtitle" id="ecomSubtitle">Venda Efetiva</span>
            </div>
            <span class="hero-part-badge" id="ecomPartBadge">Part: {kpis['ecommerce_total']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="ecomMainVal">{fmt_curr(kpis['ecommerce_total']['venda'])}</span>
            <span class="hero-meta-mes">Meta Mês: <strong id="ecomMetaMes">{kpis['ecommerce_total']['meta_mes']/1e6:.3f} Mi</strong></span>
          </div>
          <div class="hero-meta-pill" id="ecomMetaPill">
            <span>Meta: <strong id="ecomMetaMTD">{fmt_curr(kpis['ecommerce_total']['meta_mtd'])}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['ecommerce_total']['desvio_venda_pct']>=0 else 'val-negative'}" id="ecomDesvioPct">{fmt_pct(kpis['ecommerce_total']['desvio_venda_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="ecomDesvioVal">{fmt_gap(kpis['ecommerce_total']['gap_venda_val'])}</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="{'val-positive' if kpis['ecommerce_total']['evo_yoy']>=0 else 'val-negative'}" id="ecomEvol">{fmt_growth(kpis['ecommerce_total']['evo_yoy'])}</strong></span>
            <span class="indicator-item">Crescimento: <strong class="{'val-positive' if kpis['ecommerce_total']['cresc_mom']>=0 else 'val-negative'}" id="ecomCresc">{fmt_growth(kpis['ecommerce_total']['cresc_mom'])}</strong></span>
          </div>
          <div class="hero-tkm-box {'positive' if kpis['ecommerce_total']['tkm_desvio_pct']>=0 else ''}" id="ecomTkmBox">
            <span>Ticket Médio: <strong id="ecomTkm">{kpis['ecommerce_total']['tkm']:.2f}</strong></span>
            <span>Meta: <strong id="ecomTkmMeta">{kpis['ecommerce_total']['tkm_meta']:.2f}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['ecommerce_total']['tkm_desvio_pct']>=0 else 'val-negative'}" id="ecomTkmDesvioPct">{fmt_pct(kpis['ecommerce_total']['tkm_desvio_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="ecomTkmDesvioVal">{fmt_gap(kpis['ecommerce_total']['tkm_gap_val'])}</strong></span>
          </div>
        </div>

        <!-- Card 2: CANAIS DIGITAIS -->
        <div class="hero-card highlight-card" id="cardDigitais">
          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3>Canais Digitais</h3>
                <span class="badge-figital-pill" id="digFigitalBadge" style="display: none;">+ Figital</span>
              </div>
              <span class="hero-subtitle" id="digSubtitle">Site + App + Marketplace</span>
            </div>
            <span class="hero-part-badge" id="digPartBadge">Part: {kpis['canais_digitais']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="digMainVal">{fmt_curr(kpis['canais_digitais']['venda'])}</span>
            <span class="hero-meta-mes">Meta Mês: <strong id="digMetaMes">{kpis['canais_digitais']['meta_mes']/1e6:.3f} Mi</strong></span>
          </div>
          <div class="hero-meta-pill" id="digMetaPill">
            <span>Meta: <strong id="digMetaMTD">{fmt_curr(kpis['canais_digitais']['meta_mtd'])}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['canais_digitais']['desvio_venda_pct']>=0 else 'val-negative'}" id="digDesvioPct">{fmt_pct(kpis['canais_digitais']['desvio_venda_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="digDesvioVal">{fmt_gap(kpis['canais_digitais']['gap_venda_val'])}</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="{'val-positive' if kpis['canais_digitais']['evo_yoy']>=0 else 'val-negative'}" id="digEvol">{fmt_growth(kpis['canais_digitais']['evo_yoy'])}</strong></span>
            <span class="indicator-item">Crescimento: <strong class="{'val-positive' if kpis['canais_digitais']['cresc_mom']>=0 else 'val-negative'}" id="digCresc">{fmt_growth(kpis['canais_digitais']['cresc_mom'])}</strong></span>
            <span class="indicator-item">Rent. Op: <strong id="digRentOp">{kpis['canais_digitais']['rent_op']:.2f}%</strong></span>
            <span class="indicator-item">Rent. DRE: <strong id="digRentDre">{kpis['canais_digitais']['rent_dre']:.2f}%</strong></span>
          </div>
          <div class="hero-tkm-box {'positive' if kpis['canais_digitais']['tkm_desvio_pct']>=0 else ''}" id="digTkmBox">
            <span>Ticket Médio: <strong id="digTkm">{kpis['canais_digitais']['tkm']:.2f}</strong></span>
            <span>Meta: <strong id="digTkmMeta">{kpis['canais_digitais']['tkm_meta']:.2f}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['canais_digitais']['tkm_desvio_pct']>=0 else 'val-negative'}" id="digTkmDesvioPct">{fmt_pct(kpis['canais_digitais']['tkm_desvio_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="digTkmDesvioVal">{fmt_gap(kpis['canais_digitais']['tkm_gap_val'])}</strong></span>
          </div>
        </div>

        <!-- Card 3: TELEVENDAS -->
        <div class="hero-card" id="cardTelevendas">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Televendas</h3>
              <span class="hero-subtitle" id="teleSubtitle">Venda Efetiva</span>
            </div>
            <span class="hero-part-badge" id="telePartBadge">Part: {kpis['televendas']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="teleMainVal">{fmt_curr(kpis['televendas']['venda'])}</span>
            <span class="hero-meta-mes">Meta Mês: <strong id="teleMetaMes">{kpis['televendas']['meta_mes']/1e6:.3f} Mi</strong></span>
          </div>
          <div class="hero-meta-pill" id="teleMetaPill">
            <span>Meta: <strong id="teleMetaMTD">{fmt_curr(kpis['televendas']['meta_mtd'])}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['televendas']['desvio_venda_pct']>=0 else 'val-negative'}" id="teleDesvioPct">{fmt_pct(kpis['televendas']['desvio_venda_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="teleDesvioVal">{fmt_gap(kpis['televendas']['gap_venda_val'])}</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="{'val-positive' if kpis['televendas']['evo_yoy']>=0 else 'val-negative'}" id="teleEvol">{fmt_growth(kpis['televendas']['evo_yoy'])}</strong></span>
            <span class="indicator-item">Crescimento: <strong class="{'val-positive' if kpis['televendas']['cresc_mom']>=0 else 'val-negative'}" id="teleCresc">{fmt_growth(kpis['televendas']['cresc_mom'])}</strong></span>
          </div>
          <div class="hero-tkm-box {'positive' if kpis['televendas']['tkm_desvio_pct']>=0 else ''}" id="teleTkmBox">
            <span>Ticket Médio: <strong id="teleTkm">{kpis['televendas']['tkm']:.2f}</strong></span>
            <span>Meta: <strong id="teleTkmMeta">{kpis['televendas']['tkm_meta']:.2f}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['televendas']['tkm_desvio_pct']>=0 else 'val-negative'}" id="teleTkmDesvioPct">{fmt_pct(kpis['televendas']['tkm_desvio_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="teleTkmDesvioVal">{fmt_gap(kpis['televendas']['tkm_gap_val'])}</strong></span>
          </div>
        </div>

        <!-- Card 4: FIGITAL (NOVO PILAR) -->
        <div class="hero-card figital-card" id="cardFigital">
          <!-- Switch Bar ON / OFF em cima no bloco do Figital -->
          <div class="figital-switch-bar" id="figitalSwitchBar" title="Clique para Alternar: Incorporar Figital aos Totais de Canais Digitais e E-Commerce">
            <div class="figital-switch-info">
              <span class="switch-pulse-indicator"></span>
              <div class="switch-text-group">
                <span class="switch-title-text">Somar aos Totais</span>
                <span class="switch-desc-text">Digitais & E-Commerce</span>
              </div>
            </div>
            <div class="figital-switch-action">
              <span class="switch-mode-tag" id="figitalStateBadge">OFF</span>
              <label class="apple-switch" onclick="event.stopPropagation()">
                <input type="checkbox" id="toggleFigitalInput" aria-label="Somar Figital aos Totais">
                <span class="apple-slider"></span>
              </label>
            </div>
          </div>

          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3>Figital (Omnichannel)</h3>
                <span class="badge-figital-pill" id="figitalCardStatusBadge" style="display: none;">Integrado</span>
              </div>
              <span class="hero-subtitle">Lojas Integradas & Clique e Retire</span>
            </div>
            <span class="hero-part-badge" id="figitalPartBadge" style="background: var(--badge-purple-bg); color: var(--badge-purple-text);">Part: {kpis['figital']['share_empresa']:.2f}%</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="figitalMainVal">{fmt_curr(kpis['figital']['venda'])}</span>
            <span class="hero-meta-mes">Meta Mês: <strong id="figitalMetaMes">{kpis['figital']['meta_mes']/1e6:.3f} Mi</strong></span>
          </div>
          <div class="hero-meta-pill" id="figitalMetaPill">
            <span>Meta: <strong id="figitalMetaMTD">{fmt_curr(kpis['figital']['meta_mtd'])}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['figital']['desvio_venda_pct']>=0 else 'val-negative'}" id="figitalDesvioPct">{fmt_pct(kpis['figital']['desvio_venda_pct'])}</strong></span>
            <span>Cupons: <strong id="figitalCuponsVal">{kpis['figital']['cupons']:,}</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Evolução: <strong class="{'val-positive' if kpis['figital']['evo_yoy']>=0 else 'val-negative'}" id="figitalEvol">{fmt_growth(kpis['figital']['evo_yoy'])}</strong></span>
            <span class="indicator-item">Crescimento: <strong class="{'val-positive' if kpis['figital']['cresc_mom']>=0 else 'val-negative'}" id="figitalCresc">{fmt_growth(kpis['figital']['cresc_mom'])}</strong></span>
            <span class="indicator-item">Rent. Op: <strong id="figitalRentOp">{kpis['figital']['rent_op']:.2f}%</strong></span>
          </div>
          <div class="hero-tkm-box {'positive' if kpis['figital']['tkm_desvio_pct']>=0 else ''}" id="figitalTkmBox">
            <span>Ticket Médio: <strong id="figitalTkm">{kpis['figital']['tkm']:.2f}</strong></span>
            <span>Meta: <strong id="figitalTkmMeta">{kpis['figital']['tkm_meta']:.2f}</strong></span>
            <span>Desvio (%): <strong class="{'val-positive' if kpis['figital']['tkm_desvio_pct']>=0 else 'val-negative'}" id="figitalTkmDesvioPct">{fmt_pct(kpis['figital']['tkm_desvio_pct'])}</strong></span>
            <span>Desvio (R$): <strong id="figitalTkmDesvioVal">{fmt_gap(kpis['figital']['tkm_gap_val'])}</strong></span>
          </div>
        </div>
      </div>

      <!-- Detalhamento por Canal (Site, App, Marketplace) -->
      <div class="channels-grid">
        <!-- SITE -->
        <div class="channel-card">
          <div class="channel-header">
            <h4>SITE</h4>
            <span class="channel-venda-sub">Venda: <strong id="site-header-venda">{fmt_curr(kpis['site']['venda'])}</strong> (Part: <span id="site-header-share">{kpis['site']['share_empresa']:.2f}%</span>)</span>
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
            <tbody id="siteTableBody">
              {site_table_rows}
            </tbody>
          </table>
        </div>

        <!-- APP -->
        <div class="channel-card">
          <div class="channel-header">
            <h4>APP</h4>
            <span class="channel-venda-sub">Venda: <strong id="app-header-venda">{fmt_curr(kpis['app']['venda'])}</strong> (Part: <span id="app-header-share">{kpis['app']['share_empresa']:.2f}%</span>)</span>
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
            <tbody id="appTableBody">
              {app_table_rows}
            </tbody>
          </table>
        </div>

        <!-- MARKETPLACE -->
        <div class="channel-card">
          <div class="channel-header">
            <h4>MARKETPLACE</h4>
            <span class="channel-venda-sub">Venda: <strong id="mkp-header-venda">{fmt_curr(kpis['marketplace']['venda'])}</strong> (Part: <span id="mkp-header-share">{kpis['marketplace']['share_empresa']:.2f}%</span>)</span>
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
            <tbody id="mkpTableBody">
              {mkp_table_rows}
            </tbody>
          </table>
        </div>

        <!-- Combined Bar: SITE E APP -->
        <div class="combined-bar">
          <div class="combined-title">
            <span>SITE E APP</span>
            <span>Venda Efetiva: <strong id="site_app-venda">{fmt_curr(kpis['site_app']['venda'])}</strong></span>
          </div>
          <div class="combined-metrics">
            <span>Meta: <strong id="site_app-meta">{fmt_curr(kpis['site_app']['meta_mtd'])}</strong></span>
            <span>Meta Mês: <strong id="site_app-metames">{kpis['site_app']['meta_mes']/1e6:.2f} Mi</strong></span>
            <span>Desvio %: <strong class="{'val-positive' if kpis['site_app']['desvio_venda_pct']>=0 else 'val-negative'}" id="site_app-desvio">{fmt_pct(kpis['site_app']['desvio_venda_pct'])}</strong></span>
            <span>Desvio Nº: <strong id="site_app-gap">{fmt_gap(kpis['site_app']['gap_venda_val'])}</strong></span>
            <span>Evolução: <strong class="{'val-positive' if kpis['site_app']['evo_yoy']>=0 else 'val-negative'}" id="site_app-evo">{fmt_growth(kpis['site_app']['evo_yoy'])}</strong></span>
            <span>Crescimento: <strong class="{'val-positive' if kpis['site_app']['cresc_mom']>=0 else 'val-negative'}" id="site_app-cresc">{fmt_growth(kpis['site_app']['cresc_mom'])}</strong></span>
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
          <button class="pill-btn" data-channel="canais_digitais" id="btnPillCanaisDigitais">Canais Digitais (Total)</button>
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
            Cálculo estatístico do faturamento necessário por dia para alcançar 100% da meta de Setembro/2026 nos {dias_restantes} dias restantes.
          </p>
        </div>
      </div>

      <div class="projection-grid">
        {proj_cards_html}
      </div>
    </section>
  </main>

  <!-- JAVASCRIPT LOGIC -->
  <script>
    const dashData = {data_json_str};
    console.log("Dados consolidados carregados:", dashData);

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

    // Formatação de Valores
    function fmtCurrency(val) {{
      if (val === null || val === undefined) return 'R$ 0,00';
      const absVal = Math.abs(val);
      if (absVal >= 1e6) return 'R$ ' + (val / 1e6).toFixed(3).replace('.', ',') + ' Mi';
      if (absVal >= 1e3) return 'R$ ' + (val / 1e3).toFixed(1).replace('.', ',') + ' K';
      return 'R$ ' + val.toFixed(2).replace('.', ',');
    }}

    function fmtGapVal(val) {{
      if (val === null || val === undefined) return '0,00';
      const sign = val >= 0 ? '+' : '';
      const absVal = Math.abs(val);
      if (absVal >= 1e6) return sign + (val / 1e6).toFixed(3).replace('.', ',') + ' Mi';
      if (absVal >= 1e3) return sign + (val / 1e3).toFixed(1).replace('.', ',') + ' K';
      return sign + val.toFixed(2).replace('.', ',');
    }}

    function fmtPctStr(val) {{
      if (val === null || val === undefined) return '0,00%';
      const sign = val >= 0 ? '+' : '';
      return sign + val.toFixed(2).replace('.', ',') + '%';
    }}

    function fmtGrowthStr(val) {{
      if (val === null || val === undefined) return '—';
      if (val >= 0) return '⇑ ' + val.toFixed(1).replace('.', ',') + '%';
      return '⇓ ' + Math.abs(val).toFixed(1).replace('.', ',') + '%';
    }}

    // =========================================================================
    // MOTOR DE ESTADO REATIVO: FILTRO DE DATA & TOGGLE FIGITAL
    // =========================================================================
    let currentPeriod = 'mtd';
    let currentDay = dashData.max_dia || 17;
    let isFigitalOn = localStorage.getItem('fsj_figital_included') === 'true';

    const periodFilter = document.getElementById('periodFilter');
    const daySelectBox = document.getElementById('daySelectBox');
    const dayHistorySelect = document.getElementById('dayHistorySelect');

    const toggleFigitalInput = document.getElementById('toggleFigitalInput');
    const figitalSwitchBar = document.getElementById('figitalSwitchBar');
    const figitalStateBadge = document.getElementById('figitalStateBadge');
    const cardFigital = document.getElementById('cardFigital');
    const cardEcommerce = document.getElementById('cardEcommerce');
    const cardDigitais = document.getElementById('cardDigitais');
    const ecomFigitalBadge = document.getElementById('ecomFigitalBadge');
    const digFigitalBadge = document.getElementById('digFigitalBadge');
    const figitalCardStatusBadge = document.getElementById('figitalCardStatusBadge');
    const projEcomBadge = document.getElementById('proj-ecommerce_total-figital-badge');
    const projDigBadge = document.getElementById('proj-canais_digitais-figital-badge');
    const btnPillCanaisDigitais = document.getElementById('btnPillCanaisDigitais');

    function getMetricsForCurrentSelection() {{
      let baseMetrics;
      if (currentPeriod === 'mtd') {{
        baseMetrics = dashData.kpis_mtd || dashData.kpis;
      }} else if (currentPeriod === 'd1') {{
        baseMetrics = dashData.kpis_d1;
      }} else if (currentPeriod === 'last7') {{
        baseMetrics = dashData.kpis_last7;
      }} else if (currentPeriod === 'day') {{
        baseMetrics = dashData.daily_history ? dashData.daily_history[currentDay] : dashData.kpis_d1;
      }} else {{
        baseMetrics = dashData.kpis_mtd || dashData.kpis;
      }}

      // Clone
      const m = JSON.parse(JSON.stringify(baseMetrics || {{}}));

      // Se Figital estiver ativado, soma ao E-Commerce e aos Canais Digitais
      if (isFigitalOn && m.figital) {{
        // Canais Digitais (+ Figital)
        if (m.canais_digitais) {{
          m.canais_digitais.venda += m.figital.venda;
          m.canais_digitais.meta_mtd += m.figital.meta_mtd;
          m.canais_digitais.meta_mes += m.figital.meta_mes;
          m.canais_digitais.cupons += m.figital.cupons;
          m.canais_digitais.gap_venda_val = m.canais_digitais.venda - m.canais_digitais.meta_mtd;
          m.canais_digitais.desvio_venda_pct = m.canais_digitais.meta_mtd > 0 ? Number((((m.canais_digitais.venda / m.canais_digitais.meta_mtd) - 1) * 100).toFixed(2)) : 0;
          m.canais_digitais.tkm = m.canais_digitais.cupons > 0 ? Number((m.canais_digitais.venda / m.canais_digitais.cupons).toFixed(2)) : m.canais_digitais.tkm;
          m.canais_digitais.share_empresa = Number((m.canais_digitais.share_empresa + m.figital.share_empresa).toFixed(2));
          m.canais_digitais.rent_op = Number((m.canais_digitais.rent_op * 0.95 + m.figital.rent_op * 0.05).toFixed(2));
          m.canais_digitais.rent_dre = Number((m.canais_digitais.rent_op + 5.03).toFixed(2));
        }}

        // E-Commerce Total (+ Figital)
        if (m.ecommerce_total) {{
          m.ecommerce_total.venda += m.figital.venda;
          m.ecommerce_total.meta_mtd += m.figital.meta_mtd;
          m.ecommerce_total.meta_mes += m.figital.meta_mes;
          m.ecommerce_total.cupons += m.figital.cupons;
          m.ecommerce_total.gap_venda_val = m.ecommerce_total.venda - m.ecommerce_total.meta_mtd;
          m.ecommerce_total.desvio_venda_pct = m.ecommerce_total.meta_mtd > 0 ? Number((((m.ecommerce_total.venda / m.ecommerce_total.meta_mtd) - 1) * 100).toFixed(2)) : 0;
          m.ecommerce_total.tkm = m.ecommerce_total.cupons > 0 ? Number((m.ecommerce_total.venda / m.ecommerce_total.cupons).toFixed(2)) : m.ecommerce_total.tkm;
          m.ecommerce_total.share_empresa = Number((m.ecommerce_total.share_empresa + m.figital.share_empresa).toFixed(2));
        }}
      }}

      return m;
    }}

    function updateDashboardState() {{
      const m = getMetricsForCurrentSelection();
      if (!m || !m.ecommerce_total) return;

      const setTxt = (id, val) => {{
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      }};

      const setClass = (id, cls) => {{
        const el = document.getElementById(id);
        if (el) {{
          el.classList.remove('val-positive', 'val-negative');
          el.classList.add(cls);
        }}
      }};

      // 1. Atualiza Card 1: E-Commerce
      setTxt('ecomSubtitle', isFigitalOn ? 'Venda Efetiva + Figital' : 'Venda Efetiva');
      setTxt('ecomPartBadge', 'Part: ' + m.ecommerce_total.share_empresa.toFixed(2) + '%');
      setTxt('ecomMainVal', fmtCurrency(m.ecommerce_total.venda));
      setTxt('ecomMetaMes', (m.ecommerce_total.meta_mes / 1e6).toFixed(3) + ' Mi');
      setTxt('ecomMetaMTD', fmtCurrency(m.ecommerce_total.meta_mtd));
      setTxt('ecomDesvioPct', fmtPctStr(m.ecommerce_total.desvio_venda_pct));
      setClass('ecomDesvioPct', m.ecommerce_total.desvio_venda_pct >= 0 ? 'val-positive' : 'val-negative');
      setTxt('ecomDesvioVal', fmtGapVal(m.ecommerce_total.gap_venda_val));
      setTxt('ecomEvol', fmtGrowthStr(m.ecommerce_total.evo_yoy));
      setClass('ecomEvol', m.ecommerce_total.evo_yoy >= 0 ? 'val-positive' : 'val-negative');
      setTxt('ecomCresc', fmtGrowthStr(m.ecommerce_total.cresc_mom));
      setClass('ecomCresc', m.ecommerce_total.cresc_mom >= 0 ? 'val-positive' : 'val-negative');
      setTxt('ecomTkm', m.ecommerce_total.tkm.toFixed(2).replace('.', ','));
      setTxt('ecomTkmMeta', m.ecommerce_total.tkm_meta.toFixed(2).replace('.', ','));
      setTxt('ecomTkmDesvioPct', fmtPctStr(m.ecommerce_total.tkm_desvio_pct));
      setClass('ecomTkmDesvioPct', m.ecommerce_total.tkm_desvio_pct >= 0 ? 'val-positive' : 'val-negative');
      setTxt('ecomTkmDesvioVal', fmtGapVal(m.ecommerce_total.tkm_gap_val));

      // 2. Atualiza Card 2: Canais Digitais
      setTxt('digSubtitle', isFigitalOn ? 'Site + App + MKP + Figital' : 'Site + App + Marketplace');
      setTxt('digPartBadge', 'Part: ' + m.canais_digitais.share_empresa.toFixed(2) + '%');
      setTxt('digMainVal', fmtCurrency(m.canais_digitais.venda));
      setTxt('digMetaMes', (m.canais_digitais.meta_mes / 1e6).toFixed(3) + ' Mi');
      setTxt('digMetaMTD', fmtCurrency(m.canais_digitais.meta_mtd));
      setTxt('digDesvioPct', fmtPctStr(m.canais_digitais.desvio_venda_pct));
      setClass('digDesvioPct', m.canais_digitais.desvio_venda_pct >= 0 ? 'val-positive' : 'val-negative');
      setTxt('digDesvioVal', fmtGapVal(m.canais_digitais.gap_venda_val));
      setTxt('digEvol', fmtGrowthStr(m.canais_digitais.evo_yoy));
      setClass('digEvol', m.canais_digitais.evo_yoy >= 0 ? 'val-positive' : 'val-negative');
      setTxt('digCresc', fmtGrowthStr(m.canais_digitais.cresc_mom));
      setClass('digCresc', m.canais_digitais.cresc_mom >= 0 ? 'val-positive' : 'val-negative');
      setTxt('digRentOp', m.canais_digitais.rent_op.toFixed(2).replace('.', ',') + '%');
      setTxt('digRentDre', m.canais_digitais.rent_dre.toFixed(2).replace('.', ',') + '%');
      setTxt('digTkm', m.canais_digitais.tkm.toFixed(2).replace('.', ','));
      setTxt('digTkmMeta', m.canais_digitais.tkm_meta.toFixed(2).replace('.', ','));
      setTxt('digTkmDesvioPct', fmtPctStr(m.canais_digitais.tkm_desvio_pct));
      setClass('digTkmDesvioPct', m.canais_digitais.tkm_desvio_pct >= 0 ? 'val-positive' : 'val-negative');
      setTxt('digTkmDesvioVal', fmtGapVal(m.canais_digitais.tkm_gap_val));

      // 3. Atualiza Card 3: Televendas
      if (m.televendas) {{
        setTxt('telePartBadge', 'Part: ' + m.televendas.share_empresa.toFixed(2) + '%');
        setTxt('teleMainVal', fmtCurrency(m.televendas.venda));
        setTxt('teleMetaMes', (m.televendas.meta_mes / 1e6).toFixed(3) + ' Mi');
        setTxt('teleMetaMTD', fmtCurrency(m.televendas.meta_mtd));
        setTxt('teleDesvioPct', fmtPctStr(m.televendas.desvio_venda_pct));
        setClass('teleDesvioPct', m.televendas.desvio_venda_pct >= 0 ? 'val-positive' : 'val-negative');
        setTxt('teleDesvioVal', fmtGapVal(m.televendas.gap_venda_val));
        setTxt('teleEvol', fmtGrowthStr(m.televendas.evo_yoy));
        setClass('teleEvol', m.televendas.evo_yoy >= 0 ? 'val-positive' : 'val-negative');
        setTxt('teleCresc', fmtGrowthStr(m.televendas.cresc_mom));
        setClass('teleCresc', m.televendas.cresc_mom >= 0 ? 'val-positive' : 'val-negative');
        setTxt('teleTkm', m.televendas.tkm.toFixed(2).replace('.', ','));
        setTxt('teleTkmMeta', m.televendas.tkm_meta.toFixed(2).replace('.', ','));
        setTxt('teleTkmDesvioPct', fmtPctStr(m.televendas.tkm_desvio_pct));
        setClass('teleTkmDesvioPct', m.televendas.tkm_desvio_pct >= 0 ? 'val-positive' : 'val-negative');
        setTxt('teleTkmDesvioVal', fmtGapVal(m.televendas.tkm_gap_val));
      }}

      // 4. Atualiza Card 4: Figital
      if (m.figital) {{
        setTxt('figitalPartBadge', 'Part: ' + m.figital.share_empresa.toFixed(2) + '%');
        setTxt('figitalMainVal', fmtCurrency(m.figital.venda));
        setTxt('figitalMetaMes', (m.figital.meta_mes / 1e6).toFixed(3) + ' Mi');
        setTxt('figitalMetaMTD', fmtCurrency(m.figital.meta_mtd));
        setTxt('figitalDesvioPct', fmtPctStr(m.figital.desvio_venda_pct));
        setClass('figitalDesvioPct', m.figital.desvio_venda_pct >= 0 ? 'val-positive' : 'val-negative');
        setTxt('figitalCuponsVal', m.figital.cupons.toLocaleString('pt-BR'));
        setTxt('figitalEvol', fmtGrowthStr(m.figital.evo_yoy));
        setClass('figitalEvol', m.figital.evo_yoy >= 0 ? 'val-positive' : 'val-negative');
        setTxt('figitalCresc', fmtGrowthStr(m.figital.cresc_mom));
        setClass('figitalCresc', m.figital.cresc_mom >= 0 ? 'val-positive' : 'val-negative');
        setTxt('figitalRentOp', m.figital.rent_op.toFixed(2).replace('.', ',') + '%');
        setTxt('figitalTkm', m.figital.tkm.toFixed(2).replace('.', ','));
        setTxt('figitalTkmMeta', m.figital.tkm_meta.toFixed(2).replace('.', ','));
        setTxt('figitalTkmDesvioPct', fmtPctStr(m.figital.tkm_desvio_pct));
        setClass('figitalTkmDesvioPct', m.figital.tkm_desvio_pct >= 0 ? 'val-positive' : 'val-negative');
        setTxt('figitalTkmDesvioVal', fmtGapVal(m.figital.tkm_gap_val));
      }}

      // 5. Atualiza Tabelas Detalhadas de Canais (Site, App, MKP)
      ['site', 'app', 'marketplace'].forEach(chKey => {{
        const item = m[chKey];
        if (!item) return;
        setTxt(chKey + '-header-venda', fmtCurrency(item.venda));
        setTxt(chKey + '-header-share', item.share_empresa.toFixed(2) + '%');

        setTxt(chKey + '-venda-real', fmtCurrency(item.venda));
        setTxt(chKey + '-venda-meta', fmtCurrency(item.meta_mtd));
        setTxt(chKey + '-venda-desv', fmtPctStr(item.desvio_venda_pct));
        setClass(chKey + '-venda-desv', item.desvio_venda_pct >= 0 ? 'val-positive' : 'val-negative');
        setTxt(chKey + '-venda-evo', fmtGrowthStr(item.evo_yoy));
        setClass(chKey + '-venda-evo', item.evo_yoy >= 0 ? 'val-positive' : 'val-negative');
        setTxt(chKey + '-venda-cresc', fmtGrowthStr(item.cresc_mom));
        setClass(chKey + '-venda-cresc', item.cresc_mom >= 0 ? 'val-positive' : 'val-negative');

        setTxt(chKey + '-cupons-real', item.cupons >= 1e3 ? (item.cupons / 1e3).toFixed(2).replace('.', ',') + ' Mil' : item.cupons);
        setTxt(chKey + '-cupons-meta', item.cupons_meta_mtd >= 1e3 ? (item.cupons_meta_mtd / 1e3).toFixed(2).replace('.', ',') + ' Mil' : item.cupons_meta_mtd);
        setTxt(chKey + '-cupons-desv', fmtPctStr(item.cupons_desvio_pct));
        setClass(chKey + '-cupons-desv', item.cupons_desvio_pct >= 0 ? 'val-positive' : 'val-negative');

        setTxt(chKey + '-tkm-real', item.tkm.toFixed(2).replace('.', ','));
        setTxt(chKey + '-tkm-meta', item.tkm_meta.toFixed(2).replace('.', ','));
        setTxt(chKey + '-tkm-desv', fmtPctStr(item.tkm_desvio_pct));
        setClass(chKey + '-tkm-desv', item.tkm_desvio_pct >= 0 ? 'val-positive' : 'val-negative');

        setTxt(chKey + '-rent-real', item.rent_op.toFixed(2).replace('.', ',') + '%');
        setTxt(chKey + '-rent-meta', item.rent_op_meta.toFixed(2).replace('.', ',') + '%');
        setTxt(chKey + '-rent-desv', fmtPctStr(item.rent_op_desvio));
        setClass(chKey + '-rent-desv', item.rent_op_desvio >= 0 ? 'val-positive' : 'val-negative');

        if (chKey === 'site' || chKey === 'app') {{
          setTxt(chKey + '-sess-real', item.sessoes >= 1e6 ? (item.sessoes / 1e6).toFixed(2).replace('.', ',') + ' Mi' : (item.sessoes / 1e3).toFixed(0) + ' K');
          setTxt(chKey + '-sess-meta', item.sessoes_meta_mtd >= 1e6 ? (item.sessoes_meta_mtd / 1e6).toFixed(2).replace('.', ',') + ' Mi' : (item.sessoes_meta_mtd / 1e3).toFixed(0) + ' K');
          setTxt(chKey + '-sess-desv', fmtPctStr(item.sessoes_desvio_pct));
          setClass(chKey + '-sess-desv', item.sessoes_desvio_pct >= 0 ? 'val-positive' : 'val-negative');

          setTxt(chKey + '-tx-real', item.tx_conv.toFixed(2).replace('.', ',') + '%');
          setTxt(chKey + '-tx-meta', item.tx_conv_meta.toFixed(2).replace('.', ',') + '%');
          setTxt(chKey + '-tx-desv', fmtPctStr(item.tx_conv_desvio_pct));
          setClass(chKey + '-tx-desv', item.tx_conv_desvio_pct >= 0 ? 'val-positive' : 'val-negative');
        }}
      }});

      // 6. Atualiza Barra Combinada: Site e App
      if (m.site_app) {{
        setTxt('site_app-venda', fmtCurrency(m.site_app.venda));
        setTxt('site_app-meta', fmtCurrency(m.site_app.meta_mtd));
        setTxt('site_app-metames', (m.site_app.meta_mes / 1e6).toFixed(2) + ' Mi');
        setTxt('site_app-desvio', fmtPctStr(m.site_app.desvio_venda_pct));
        setClass('site_app-desvio', m.site_app.desvio_venda_pct >= 0 ? 'val-positive' : 'val-negative');
        setTxt('site_app-gap', fmtGapVal(m.site_app.gap_venda_val));
        setTxt('site_app-evo', fmtGrowthStr(m.site_app.evo_yoy));
        setClass('site_app-evo', m.site_app.evo_yoy >= 0 ? 'val-positive' : 'val-negative');
        setTxt('site_app-cresc', fmtGrowthStr(m.site_app.cresc_mom));
        setClass('site_app-cresc', m.site_app.cresc_mom >= 0 ? 'val-positive' : 'val-negative');
      }}

      // 7. Visão 4 Projeções (Atualiza valores com base em MTD ou D-1)
      ['ecommerce_total', 'canais_digitais', 'app', 'site', 'marketplace', 'figital'].forEach(chKey => {{
        if (m[chKey]) {{
          setTxt('proj-real-' + chKey, fmtCurrency(m[chKey].venda));
          const restante = Math.max(0, m[chKey].meta_mes - m[chKey].venda);
          setTxt('proj-restante-' + chKey, fmtCurrency(restante));
          const diasRest = Math.max(1, 30 - currentDay);
          const diariaNec = restante / diasRest;
          setTxt('proj-diaria-' + chKey, 'R$ ' + (diariaNec / 1e3).toFixed(0) + ' K/dia');
        }}
      }});

      // 8. Se Visão 2 estiver ativa, re-renderiza gráficos
      if (typeof renderDesviosCharts === 'function') {{
        renderDesviosCharts(currentChannelV2);
      }}
    }}

    // Aplica Toggle do Figital
    function applyFigitalToggle(included) {{
      isFigitalOn = included;
      if (toggleFigitalInput) toggleFigitalInput.checked = included;

      // Update Switch Header State
      if (figitalSwitchBar && figitalStateBadge) {{
        if (included) {{
          figitalSwitchBar.classList.add('active-on');
          figitalStateBadge.textContent = 'ON';
          if (cardFigital) cardFigital.classList.add('figital-integrated');
          if (figitalCardStatusBadge) figitalCardStatusBadge.style.display = 'inline-flex';
        }} else {{
          figitalSwitchBar.classList.remove('active-on');
          figitalStateBadge.textContent = 'OFF';
          if (cardFigital) cardFigital.classList.remove('figital-integrated');
          if (figitalCardStatusBadge) figitalCardStatusBadge.style.display = 'none';
        }}
      }}

      // Update Badges nos cards E-Com e Digitais
      if (cardEcommerce) {{
        if (included) cardEcommerce.classList.add('figital-integrated');
        else cardEcommerce.classList.remove('figital-integrated');
        if (ecomFigitalBadge) ecomFigitalBadge.style.display = included ? 'inline-flex' : 'none';
      }}

      if (cardDigitais) {{
        if (included) cardDigitais.classList.add('figital-integrated');
        else cardDigitais.classList.remove('figital-integrated');
        if (digFigitalBadge) digFigitalBadge.style.display = included ? 'inline-flex' : 'none';
      }}

      if (projEcomBadge) projEcomBadge.style.display = included ? 'inline-flex' : 'none';
      if (projDigBadge) projDigBadge.style.display = included ? 'inline-flex' : 'none';

      if (btnPillCanaisDigitais) {{
        btnPillCanaisDigitais.textContent = included ? 'Canais Digitais (+ Figital)' : 'Canais Digitais (Total)';
      }}

      localStorage.setItem('fsj_figital_included', included ? 'true' : 'false');
      updateDashboardState();
    }}

    if (figitalSwitchBar && toggleFigitalInput) {{
      figitalSwitchBar.addEventListener('click', (e) => {{
        if (e.target !== toggleFigitalInput) {{
          toggleFigitalInput.checked = !toggleFigitalInput.checked;
        }}
        applyFigitalToggle(toggleFigitalInput.checked);
      }});

      toggleFigitalInput.addEventListener('change', () => {{
        applyFigitalToggle(toggleFigitalInput.checked);
      }});
    }}

    // Eventos do Filtro de Data & Histórico
    if (periodFilter) {{
      periodFilter.addEventListener('change', (e) => {{
        currentPeriod = e.target.value;
        if (currentPeriod === 'day') {{
          if (daySelectBox) daySelectBox.style.display = 'flex';
          currentDay = parseInt(dayHistorySelect ? dayHistorySelect.value : dashData.max_dia, 10);
        }} else {{
          if (daySelectBox) daySelectBox.style.display = 'none';
          currentDay = dashData.max_dia || 17;
        }}
        updateDashboardState();
      }});
    }}

    if (dayHistorySelect) {{
      dayHistorySelect.addEventListener('change', (e) => {{
        currentDay = parseInt(e.target.value, 10);
        currentPeriod = 'day';
        updateDashboardState();
      }});
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
      let cData = dashData.charts[channelKey] || dashData.charts['marketplace'];
      if (channelKey === 'canais_digitais' && isFigitalOn && dashData.charts['figital']) {{
        const digData = dashData.charts['canais_digitais'];
        const figData = dashData.charts['figital'];
        cData = {{
          tkm: {{
            real: digData.tkm.real.map((v, i) => Number(((v * 16704 + (figData.tkm.real[i] || 142) * 592) / (16704 + 592)).toFixed(2))),
            meta: digData.tkm.meta
          }},
          rent_op: {{
            real: digData.rent_op.real.map((v, i) => Number((v * 0.95 + (figData.rent_op.real[i] || 22.4) * 0.05).toFixed(1))),
            desvio: digData.rent_op.desvio
          }},
          faturamento: {{
            real: digData.faturamento.real.map((v, i) => Math.round(v + (figData.faturamento.real[i] || 0))),
            desvio: digData.faturamento.desvio.map((v, i) => Math.round(v + (figData.faturamento.desvio ? (figData.faturamento.desvio[i] || 0) : 0)))
          }}
        }};
      }}
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

      // 2. Chart Rentabilidade Operacional
      if (chartRentInstance) chartRentInstance.destroy();
      const ctxRent = document.getElementById('chartRent').getContext('2d');
      chartRentInstance = new Chart(ctxRent, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Rentabilidade Real %',
              data: cData.rent_op.real,
              borderColor: '#0056b3',
              borderWidth: 2.8,
              fill: false,
              tension: 0.25,
              pointRadius: 5,
              pointBackgroundColor: '#0056b3',
              yAxisID: 'y',
              datalabels: {{
                display: true,
                align: 'top',
                offset: 5,
                font: {{ size: 10, weight: '700' }},
                color: () => currentTheme === 'dark' ? '#93c5fd' : '#003875',
                formatter: val => val.toFixed(1) + '%'
              }}
            }},
            {{
              label: 'Desvio % vs Meta',
              data: cData.rent_op.desvio,
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56, 189, 248, 0.12)',
              borderWidth: 2,
              borderDash: [4, 4],
              fill: true,
              tension: 0.25,
              pointRadius: 4,
              yAxisID: 'y1',
              datalabels: {{
                display: true,
                align: 'bottom',
                offset: 5,
                font: {{ size: 9, weight: '600' }},
                color: ctx => ctx.dataset.data[ctx.dataIndex] >= 0 ? '#16a34a' : '#dc2626',
                formatter: val => (val > 0 ? '+' : '') + val.toFixed(1) + '%'
              }}
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

      // 3. Chart Faturamento & Desvio GAP
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
              suggestedMax: 1800000,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return 'R$ ' + (val/1000).toFixed(0) + 'K'; }}
              }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
              suggestedMin: -50000,
              suggestedMax: 1800000,
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

      // 2. Chart Sessões
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
              datalabels: {{
                display: true,
                align: 'top',
                offset: 5,
                font: {{ size: 9.5, weight: '700' }},
                color: ctx => ctx.dataset.data[ctx.dataIndex] >= 0 ? '#16a34a' : '#dc2626',
                formatter: val => (val > 0 ? '+' : '') + val.toFixed(1) + '%'
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
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return (val/1000).toFixed(0) + 'K'; }}
              }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
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

    // Inicialização da UI com preferências salvas
    applyFigitalToggle(isFigitalOn);
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
