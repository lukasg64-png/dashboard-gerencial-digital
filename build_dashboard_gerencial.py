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
    visao_anual = dash_data.get('visao_anual', {})
    ytd = visao_anual.get('ytd', {})
    meses_anual = visao_anual.get('meses', [])

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

    # Precomputações YTD
    ytd_dig = ytd.get('digitais', {})
    ytd_ecom = ytd.get('ecommerce_sem_figital', {})
    ytd_dig_real_str = fmt_curr(ytd_dig.get('real', 0))
    ytd_dig_meta_str = fmt_curr(ytd_dig.get('meta', 0))
    ytd_dig_desvio_val_str = fmt_gap(ytd_dig.get('desvio_val', 0))
    ytd_dig_desvio_pct_str = fmt_pct(ytd_dig.get('desvio_pct', 0))
    ytd_dig_ating_str = f"{ytd_dig.get('atingimento_pct', 100.0):.1f}% Meta"
    ytd_dig_desv_cls = 'val-positive' if ytd_dig.get('desvio_val', 0) >= 0 else 'val-negative'

    ytd_ecom_real_str = fmt_curr(ytd_ecom.get('real', 0))
    ytd_ecom_meta_str = fmt_curr(ytd_ecom.get('meta', 0))
    ytd_ecom_desvio_val_str = fmt_gap(ytd_ecom.get('desvio_val', 0))
    ytd_ecom_desvio_pct_str = fmt_pct(ytd_ecom.get('desvio_pct', 0))
    ytd_ecom_ating_str = f"{ytd_ecom.get('atingimento_pct', 100.0):.1f}% Meta"
    ytd_ecom_desv_cls = 'val-positive' if ytd_ecom.get('desvio_val', 0) >= 0 else 'val-negative'

    # Totais consolidados de tráfego GA4
    tot_sessoes_ga = sum(o.get('sessoes', 0) for o in origens)
    tot_pedidos_ga = sum(o.get('pedidos', 0) for o in origens)
    tot_receita_ga = sum(o.get('receita', 0.0) for o in origens)
    tot_tx_conv_ga = (tot_pedidos_ga / tot_sessoes_ga * 100) if tot_sessoes_ga > 0 else 0.0

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

    /* ==========================================================================
       SEÇÃO DE FILTRO DE DATA OFICIAL FSJ / APPLE HIG
       ========================================================================== */
    .date-filter-section {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 14px 20px;
      margin-bottom: 22px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: var(--transition);
    }}

    .date-filter-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}

    .date-filter-inputs-group {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .date-filter-title {{
      font-size: 13px;
      font-weight: 800;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 6px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      font-family: 'Outfit', sans-serif;
    }}

    .date-inputs-pair {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .date-input-wrap {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-pill);
      padding: 5px 12px;
      transition: var(--transition);
    }}

    .date-input-wrap:focus-within {{
      border-color: var(--fsj-blue);
      box-shadow: 0 0 0 2px rgba(0, 119, 255, 0.15);
    }}

    .date-input-wrap label {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .apple-date-input {{
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    .apple-date-input::-webkit-calendar-picker-indicator {{
      filter: invert(0.5);
      cursor: pointer;
    }}

    .date-range-separator {{
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 600;
    }}

    .date-presets-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .preset-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      font-weight: 700;
      background: var(--bg-card-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-card);
      cursor: pointer;
      transition: var(--transition);
      user-select: none;
    }}

    .preset-pill:hover {{
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--fsj-blue);
      transform: translateY(-1px);
    }}

    .preset-pill.active {{
      background: var(--fsj-blue) !important;
      color: #ffffff !important;
      border-color: var(--fsj-blue) !important;
      box-shadow: 0 2px 10px rgba(0, 119, 255, 0.35);
    }}

    .date-period-badge {{
      font-size: 12px;
      font-weight: 700;
      padding: 6px 16px;
      border-radius: var(--radius-pill);
      background: rgba(0, 119, 255, 0.10);
      color: var(--fsj-blue);
      border: 1px solid rgba(0, 119, 255, 0.25);
    }}

    /* Toggle MoM vs YoY no Diagnóstico */
    .diag-toggle-group {{
      display: inline-flex;
      align-items: center;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-pill);
      padding: 3px;
      gap: 3px;
    }}

    .diag-toggle-btn {{
      border: none;
      background: transparent;
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      font-weight: 700;
      color: var(--text-secondary);
      cursor: pointer;
      transition: var(--transition);
    }}

    .diag-toggle-btn:hover {{
      color: var(--text-primary);
    }}

    .diag-toggle-btn.active {{
      background: #ffffff;
      color: var(--fsj-blue);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}

    body.dark-mode .diag-toggle-btn.active {{
      background: var(--fsj-blue);
      color: #ffffff;
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

    /* ==========================================================================
       VISÃO ANUAL 2026 & DIAGNÓSTICO MENSAL DE INVOLUÇÕES (APPLE DESIGN)
       ========================================================================== */
    .annual-banner-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 20px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .annual-banner-card::before {{
      content: "";
      position: absolute;
      top: 0; left: 0; bottom: 0; width: 5px;
      background: var(--fsj-blue-gradient);
    }}

    .banner-badge {{
      display: inline-flex;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      background: rgba(0, 119, 255, 0.1);
      color: var(--fsj-blue-light);
      margin-bottom: 6px;
    }}

    .annual-banner-content h2 {{
      font-family: 'Outfit', sans-serif;
      font-size: 20px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }}

    .annual-banner-content p {{
      font-size: 13px;
      color: var(--text-secondary);
      max-width: 820px;
      line-height: 1.5;
    }}

    .banner-action-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--fsj-blue-gradient);
      color: #ffffff;
      border: none;
      padding: 10px 18px;
      border-radius: var(--radius-pill);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 86, 179, 0.25);
      transition: var(--transition);
    }}

    .banner-action-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 86, 179, 0.35);
    }}

    /* Pílulas de Seleção de Mês */
    .month-selector-bar {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: var(--shadow-sm);
    }}

    .month-selector-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .month-pills-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .month-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 16px;
      border-radius: var(--radius-pill);
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      font-size: 13px;
      font-weight: 700;
      color: var(--text-primary);
      cursor: pointer;
      transition: var(--transition);
      user-select: none;
    }}

    .month-pill:hover {{
      border-color: var(--fsj-blue-light);
      background: var(--bg-card-hover);
      transform: translateY(-1px);
    }}

    .month-pill.active {{
      background: var(--fsj-blue-gradient);
      color: #ffffff;
      border-color: transparent;
      box-shadow: 0 4px 14px rgba(0, 119, 255, 0.35);
    }}

    .pill-badge {{
      font-size: 10px;
      padding: 2px 7px;
      border-radius: 10px;
      font-weight: 800;
    }}

    .month-pill.active .pill-badge {{
      background: rgba(255, 255, 255, 0.25);
      color: #ffffff;
    }}

    .pill-badge.badge-success {{ background: var(--badge-green-bg); color: var(--badge-green-text); }}
    .pill-badge.badge-warning {{ background: #fef3c7; color: #b45309; }}
    .pill-badge.badge-danger {{ background: var(--badge-red-bg); color: var(--badge-red-text); }}

    /* Painel de Diagnóstico Executivo */
    .diagnostic-panel-container {{
      display: flex;
      flex-direction: column;
      gap: 18px;
      animation: fadeIn 0.3s ease;
    }}

    .diag-header-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 20px 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 18px;
    }}

    .diag-title-box h3 {{
      font-family: 'Outfit', sans-serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      margin: 6px 0 2px 0;
    }}

    .diag-title-box p {{
      font-size: 12px;
      color: var(--text-secondary);
    }}

    /* Toggle MoM vs YoY Segment Control */
    .diag-toggle-group {{
      display: inline-flex;
      align-items: center;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-pill);
      padding: 3px;
      gap: 4px;
    }}

    .diag-toggle-btn {{
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-size: 11.5px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      cursor: pointer;
      transition: var(--transition);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .diag-toggle-btn:hover {{
      color: var(--text-primary);
    }}

    .diag-toggle-btn.active {{
      background: var(--fsj-blue-gradient);
      color: #ffffff;
      box-shadow: 0 2px 8px rgba(0, 86, 179, 0.25);
    }}

    .diag-kpi-summary {{
      display: flex;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }}

    .diag-kpi-item {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .diag-kpi-item .lbl {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--text-secondary);
    }}

    .diag-kpi-item .val {{
      font-size: 16px;
      font-weight: 800;
      color: var(--text-primary);
    }}

    .btn-jump-diario {{
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      color: var(--fsj-blue);
      font-size: 12px;
      font-weight: 700;
      padding: 8px 14px;
      border-radius: var(--radius-pill);
      cursor: pointer;
      transition: var(--transition);
    }}

    .btn-jump-diario:hover {{
      background: var(--fsj-blue);
      color: #ffffff;
      border-color: var(--fsj-blue);
    }}

    /* Grid de 3 Colunas de Diagnóstico */
    .diag-grid {{
      display: grid;
      grid-template-columns: 1.15fr 0.95fr 0.95fr;
      gap: 18px;
    }}

    @media (max-width: 1280px) {{
      .diag-grid {{ grid-template-columns: 1fr; }}
    }}

    .diag-col-card {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 18px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .diag-col-card.alert-border {{
      border-top: 3.5px solid #ef4444;
    }}

    .diag-col-card.success-border {{
      border-top: 3.5px solid #10b981;
    }}

    .diag-col-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-card);
    }}

    .diag-col-header h4 {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 2px;
    }}

    .diag-col-header p {{
      font-size: 11.5px;
      color: var(--text-secondary);
    }}

    .badge-count {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--bg-card-subtle);
      color: var(--text-secondary);
    }}

    .badge-count.badge-danger {{
      background: var(--badge-red-bg);
      color: var(--badge-red-text);
    }}

    .badge-count.badge-success {{
      background: var(--badge-green-bg);
      color: var(--badge-green-text);
    }}

    /* Tabela de Grupos Diagnóstico */
    .diag-table-wrapper {{
      overflow-x: auto;
    }}

    .diag-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
    }}

    .diag-table th {{
      background: var(--bg-card-subtle);
      padding: 8px 10px;
      font-weight: 700;
      color: var(--text-secondary);
      border-bottom: 1px solid var(--border-card);
      white-space: nowrap;
    }}

    .diag-table td {{
      padding: 9px 10px;
      border-bottom: 1px solid var(--border-card);
      color: var(--text-primary);
      white-space: nowrap;
    }}

    .diag-table tr:hover td {{
      background: var(--bg-card-subtle);
    }}

    /* Linhas Cards */
    .diag-lines-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 480px;
      overflow-y: auto;
      padding-right: 4px;
    }}

    .line-card-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 12px;
      border-radius: 10px;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      transition: var(--transition);
    }}

    .line-card-item:hover {{
      transform: translateX(3px);
      background: var(--bg-card-hover);
      border-color: var(--fsj-blue-light);
    }}

    .line-info-left {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .line-name {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .line-meta {{
      font-size: 11px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .line-grp-tag {{
      font-size: 9.5px;
      font-weight: 700;
      padding: 1px 5px;
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.05);
      color: var(--text-secondary);
    }}

    .line-delta-pill {{
      text-align: right;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 1px;
    }}

    .line-delta-pill .val {{
      font-size: 13px;
      font-weight: 800;
    }}

    .line-delta-pill .pct {{
      font-size: 11px;
      font-weight: 700;
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
      <!-- Visão 0: Visão Anual 2026 & Diagnóstico -->
      <button class="nav-btn active" data-view="view-anual" title="Visão Anual 2026 & Diagnóstico de Involuções">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </button>

      <!-- Visão 1: Visão Geral -->
      <button class="nav-btn" data-view="view-geral" title="Visão Geral & Cards Executivos MTD/Diário">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
      </button>

      <!-- Visão 2: Tendências & Desvios Diários -->
      <button class="nav-btn" data-view="view-desvios" title="Tendências & Desvios Diários">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
        </svg>
      </button>

      <!-- Visão 3: Tráfego e Conversão -->
      <button class="nav-btn" data-view="view-trafego" title="Tráfego, Conversão e Origens">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </button>

      <!-- Visão 4: Projeção & Run Rate -->
      <button class="nav-btn" data-view="view-projecoes" title="Projeção de Fechamento & Fechamento Mês">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
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
        <!-- TOGGLE INTEGRAR FIGITAL (GLOBAL) -->
        <div class="figital-switch-bar" id="figitalSwitchBar" title="Clique para Alternar: Incorporar Figital aos Totais de Canais Digitais e E-Commerce">
          <div class="figital-switch-info">
            <span class="switch-pulse-indicator"></span>
            <div class="switch-text-group">
              <span class="switch-title-text">+ Figital</span>
              <span class="switch-desc-text">Integrar Totais</span>
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

        <button class="theme-toggle-btn" id="themeBtn" title="Alternar Modo Escuro/Claro">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- ====================================================================
         SEÇÃO DE FILTRO DE DATA OFICIAL (APPLE HIG / FARMÁCIAS SÃO JOÃO)
         ==================================================================== -->
    <section class="date-filter-section" id="dateFilterSection">
      <div class="date-filter-row">
        <div class="date-filter-inputs-group">
          <span class="date-filter-title">📅 Período de Análise:</span>
          <div class="date-inputs-pair">
            <div class="date-input-wrap">
              <label for="filterDateIni">Início</label>
              <input type="date" id="filterDateIni" class="apple-date-input" min="2026-09-01" max="2026-09-{max_dia:02d}" value="2026-09-01" onchange="onDateInputChange()">
            </div>
            <span class="date-range-separator">até</span>
            <div class="date-input-wrap">
              <label for="filterDateEnd">Fim</label>
              <input type="date" id="filterDateEnd" class="apple-date-input" min="2026-09-01" max="2026-09-{max_dia:02d}" value="2026-09-{max_dia:02d}" onchange="onDateInputChange()">
            </div>
          </div>
        </div>

        <div class="date-presets-group">
          <span class="preset-pill active" id="presetMtd" onclick="selectDatePreset('mtd')">⭐ Mês Acumulado (MTD D-1)</span>
          <span class="preset-pill" id="presetYesterday" onclick="selectDatePreset('yesterday')">⚡ Ontem (D-1)</span>
          <span class="preset-pill" id="preset7Days" onclick="selectDatePreset('7days')">📆 Últimos 7 Dias</span>
          <span class="preset-pill" id="presetThisWeek" onclick="selectDatePreset('this_week')">🗓️ Semana Atual</span>
        </div>

        <div class="date-period-badge" id="datePeriodInfo">
          <span>01 a {max_dia:02d}/09/2026 ({max_dia} dias MTD D-1)</span>
        </div>
      </div>
    </section>

    <!-- ====================================================================
         VISÃO 0: VISÃO ANUAL 2026 & DIAGNÓSTICO MENSAL DE INVOLUÇÕES
         ==================================================================== -->
    <section class="view-panel active" id="view-anual">
      <!-- Banner Estratégico Superior -->
      <div class="annual-banner-card">
        <div class="annual-banner-content">
          <div class="banner-badge">Visão Executiva YTD 2026</div>
          <h2>Consolidado Anual 2026 — Canais Digitais & Figital</h2>
          <p>Evolução acumulada de Janeiro a Setembro, comparativo de metas mês a mês e diagnóstico analítico de involuções por categoria e linha de produto.</p>
        </div>
        <div class="annual-banner-actions">
          <button class="banner-action-btn" id="btnSwitchToGeral" onclick="switchView('view-geral')">
            <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
            Ir para Acompanhamento Diário / MTD
          </button>
        </div>
      </div>

      <!-- 4 Hero Cards Anuais (YTD) -->
      <div class="top-hero-grid">
        <!-- Card 1: Faturamento Digital YTD -->
        <div class="hero-card highlight-card" id="cardAnualDigital">
          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3>Canais Digitais (YTD)</h3>
                <span class="badge-figital-pill" id="ytdDigFigitalBadge" style="display: none;">+ Figital</span>
              </div>
              <span class="hero-subtitle">Acumulado Jan a Set/2026</span>
            </div>
            <span class="hero-part-badge" style="background: var(--badge-green-bg); color: var(--badge-green-text);" id="ytdDigAting">
              {ytd_dig_ating_str}
            </span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="ytdDigReal">{ytd_dig_real_str}</span>
            <span class="hero-meta-mes">Meta YTD: <strong id="ytdDigMeta">{ytd_dig_meta_str}</strong></span>
          </div>
          <div class="hero-meta-pill">
            <span>Desvio (R$): <strong id="ytdDigDesvioVal" class="{ytd_dig_desv_cls}">{ytd_dig_desvio_val_str}</strong></span>
            <span>Desvio (%): <strong id="ytdDigDesvioPct" class="{ytd_dig_desv_cls}">{ytd_dig_desvio_pct_str}</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Crescimento YoY: <strong class="val-positive">⇑ +43.8%</strong></span>
            <span class="indicator-item">Meses Acima da Meta: <strong class="val-positive">5 de 9</strong></span>
          </div>
        </div>

        <!-- Card 2: E-Commerce Total YTD -->
        <div class="hero-card highlight-card" id="cardAnualEcom">
          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3>E-Commerce Total (YTD)</h3>
                <span class="badge-figital-pill" id="ytdEcomFigitalBadge" style="display: none;">+ Figital</span>
              </div>
              <span class="hero-subtitle">Digitais + Televendas</span>
            </div>
            <span class="hero-part-badge" style="background: var(--badge-green-bg); color: var(--badge-green-text);" id="ytdEcomAting">
              {ytd_ecom_ating_str}
            </span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="ytdEcomReal">{ytd_ecom_real_str}</span>
            <span class="hero-meta-mes">Meta YTD: <strong id="ytdEcomMeta">{ytd_ecom_meta_str}</strong></span>
          </div>
          <div class="hero-meta-pill">
            <span>Desvio (R$): <strong id="ytdEcomDesvioVal" class="{ytd_ecom_desv_cls}">{ytd_ecom_desvio_val_str}</strong></span>
            <span>Desvio (%): <strong id="ytdEcomDesvioPct" class="{ytd_ecom_desv_cls}">{ytd_ecom_desvio_pct_str}</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Crescimento YoY: <strong class="val-positive">⇑ +42.5%</strong></span>
            <span class="indicator-item">Pilar Figital (Set): <strong>R$ 2.762 Mi</strong></span>
          </div>
        </div>

        <!-- Card 3: Balanço de Desempenho -->
        <div class="hero-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Balanço de Metas</h3>
              <span class="hero-subtitle">Consistência Mensal 2026</span>
            </div>
            <span class="hero-part-badge" style="background: #e0f2fe; color: #0284c7;">55.6% Sucesso</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" style="color: var(--badge-green-text);">5 Meses Batidos</span>
            <span class="hero-meta-mes">4 meses em recuperação (Abr, Mai, Jun, Jul)</span>
          </div>
          <div class="hero-meta-pill">
            <span>Melhor Mês: <strong class="val-positive">Fev/26 (+109.5%)</strong></span>
            <span>Mês Recorde: <strong style="color: var(--fsj-blue-light);">Ago/26 (R$ 55.9M)</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Média Mensal: <strong>R$ 51.7 Mi/mês</strong></span>
            <span class="indicator-item">Ritmo Atual (Set): <strong class="val-positive">103.5% da Meta</strong></span>
          </div>
        </div>

        <!-- Card 4: Projeção Anual Ponderada Q4 (Black Friday + Natal) -->
        <div class="hero-card" id="cardProjAno">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Projeção de Fechamento (FY26)</h3>
              <span class="hero-subtitle" id="projSubtitle">Modelo Ponderado com Sazonalidade Q4</span>
            </div>
            <span class="hero-part-badge" id="projBadge" style="background: #fef3c7; color: #b45309;">Sazonal Q4 (BF + Natal)</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="projAnoVal" style="color: var(--fsj-blue);">~R$ 688 Mi</span>
            <span class="hero-meta-mes" id="projDesc">Expectativa Consolidada com Q4 Acelerado</span>
          </div>
          <div class="hero-meta-pill">
            <span>Meta Orçada Anual: <strong id="projMetaAno">R$ 683.0 Mi</strong></span>
            <span>Previsão Superação: <strong class="val-positive" id="projSuperacao">+R$ 5.0 Mi (+0.7%)</strong></span>
          </div>
          <div class="hero-sub-indicators">
            <span class="indicator-item">Black Friday (Nov): <strong style="color: var(--fsj-accent);">R$ 80.0 Mi (Meta Oficial)</strong></span>
            <span class="indicator-item">Dezembro (Natal): <strong style="color: #0284c7;">~R$ 77.0 Mi (Pico Histórico)</strong></span>
          </div>
        </div>
      </div>

      <!-- Gráfico Comparativo Mês a Mês: Meta vs Realizado -->
      <div class="card-chart-full">
        <div class="card-chart-header">
          <div>
            <h3>Evolução Mensal 2026 — Realizado vs Meta Oficial</h3>
            <p>Comparativo consolidado de faturamento mês a mês. Clique em qualquer coluna do gráfico ou use as opções abaixo para inspecionar o diagnóstico do mês.</p>
          </div>
          <div class="chart-legend-box">
            <div class="legend-item"><span class="legend-color" style="background: #0077ff;"></span> Realizado Digital</div>
            <div class="legend-item" id="annualLegendFigital" style="display: none;"><span class="legend-color" style="background: #8b5cf6;"></span> Figital</div>
            <div class="legend-item"><span class="legend-color" style="background: #94a3b8; border-top: 2px dashed #003875;"></span> Meta Oficial</div>
          </div>
        </div>
        <div style="height: 320px; width: 100%; position: relative;">
          <canvas id="chartAnualMeses"></canvas>
        </div>
      </div>

      <!-- Pílulas de Seleção de Mês para Diagnóstico -->
      <div class="month-selector-bar">
        <div class="month-selector-title">
          <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"/>
          </svg>
          Selecione o Mês para Diagnóstico de Involuções:
        </div>
        <div class="month-pills-list" id="annualMonthPills">
          <!-- Gerado dinamicamente via JS com status de cor -->
        </div>
      </div>

      <!-- PAINEL DE DIAGNÓSTICO DO MÊS SELECIONADO -->
      <div class="diagnostic-panel-container" id="diagnosticPanel">
        <!-- Header do Mês Selecionado -->
        <div class="diag-header-card">
          <div class="diag-title-box">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
              <span class="diag-badge-pill" id="diagStatusBadge">🟢 Meta Superada</span>
              <div class="diag-toggle-group">
                <button class="diag-toggle-btn active" id="btnDiagMoM" onclick="setDiagComparisonMode('mom')">
                  📅 vs Mês Anterior (MoM • Ritmo Diário)
                </button>
                <button class="diag-toggle-btn" id="btnDiagYoY" onclick="setDiagComparisonMode('yoy')">
                  🗓️ vs Ano Anterior (YoY • Evolução Anual)
                </button>
              </div>
            </div>
            <h3 id="diagMonthTitle">Diagnóstico Executivo — Setembro de 2026</h3>
            <p id="diagSubtitle">Comparativo analítico em relação a Agosto de 2026 e detalhamento de motores de crescimento e perdas.</p>
            <div class="diag-prorata-notice" id="diagProrataNotice" style="display: flex; align-items: center; gap: 8px; margin-top: 8px; padding: 6px 14px; border-radius: 8px; background: rgba(0, 119, 255, 0.08); border: 1px solid rgba(0, 119, 255, 0.2); font-size: 11.5px; color: var(--fsj-blue);">
              <span>💡</span>
              <span id="diagNoticeText"><strong>Base Normalizada Pró-rata:</strong> Para Setembro ({max_dia} dias apurados), os comparativos MoM utilizam o ritmo diário equivalente de Agosto ({max_dia} dias pró-rata: R$ 1,945 Mi/dia vs R$ 1,804 Mi/dia = +7,8%) para eliminar distorções de mês incompleto.</span>
            </div>
          </div>
          <div class="diag-kpi-summary">
            <div class="diag-kpi-item">
              <span class="lbl">Realizado Digitais</span>
              <span class="val" id="diagRealDigitais">R$ 33.065 Mi</span>
            </div>
            <div class="diag-kpi-item">
              <span class="lbl">Meta Oficial MTD</span>
              <span class="val" id="diagMetaDigitais">R$ 31.956 Mi</span>
            </div>
            <div class="diag-kpi-item">
              <span class="lbl">Desvio vs Meta</span>
              <span class="val val-positive" id="diagDesvioDigitais">+R$ 1.110 Mi (+3.47%)</span>
            </div>
            <div class="diag-kpi-item">
              <span class="lbl" id="diagMetric4Lbl">Ritmo Diário MoM</span>
              <span class="val val-positive" id="diagMoM">R$ 1,945 Mi/dia (+7,8%)</span>
            </div>
            <div class="diag-kpi-item">
              <span class="lbl">Evolução YoY</span>
              <span class="val val-positive" id="diagYoY">+60,9% vs Set/25</span>
            </div>
            <div class="diag-kpi-item" style="border-left: 1px solid var(--border-card); padding-left: 14px;">
              <button class="btn-jump-diario" id="btnJumpDiario" title="Abrir Visão Diária detalhada deste mês" onclick="switchView('view-geral')">
                Ver Acompanhamento Diário ➜
              </button>
            </div>
          </div>
        </div>

        <!-- Grid com 3 Colunas de Diagnóstico -->
        <div class="diag-grid">
          <!-- Coluna 1: Categorias / Grupos (Ranking de Involução / Desempenho) -->
          <div class="diag-col-card">
            <div class="diag-col-header">
              <div>
                <h4 id="diagCol1Title">Categorias & Grupos</h4>
                <p id="diagCol1Desc">Ordenadas pelas maiores involuções (quedas nominais vs ritmo anterior)</p>
              </div>
              <span class="badge-count" id="countGrupos">Grupos</span>
            </div>
            <div class="diag-table-wrapper">
              <table class="diag-table" id="tableGruposDiag">
                <thead>
                  <tr>
                    <th id="thColCategoria">Categoria</th>
                    <th style="text-align: right;" id="thColVenda">Venda Mês</th>
                    <th style="text-align: right;" id="thColAnt">Mês Anterior</th>
                    <th style="text-align: right;" id="thColDelta">Delta (R$)</th>
                    <th style="text-align: right;" id="thColVar">Var %</th>
                  </tr>
                </thead>
                <tbody id="tbodyGruposDiag">
                  <!-- Inserido dinamicamente via JS -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Coluna 2: Top Linhas em Involução / Queda (Ofensores) -->
          <div class="diag-col-card alert-border">
            <div class="diag-col-header">
              <div>
                <h4 style="color: #b91c1c;" id="diagCol2Title">⚠️ Linhas com Maior Queda (Ofensores)</h4>
                <p id="diagCol2Desc">Produtos/Linhas que mais puxaram o faturamento para baixo no período</p>
              </div>
              <span class="badge-count badge-danger" id="badgeCol2Tag">Top Quedas</span>
            </div>
            <div class="diag-lines-list" id="listLinhasInvolucao">
              <!-- Inserido dinamicamente via JS -->
            </div>
          </div>

          <!-- Coluna 3: Top Linhas em Evolução / Crescimento (Alavancas) -->
          <div class="diag-col-card success-border">
            <div class="diag-col-header">
              <div>
                <h4 style="color: #15803d;" id="diagCol3Title">🚀 Linhas com Maior Crescimento (Alavancas)</h4>
                <p id="diagCol3Desc">Produtos/Linhas com maior avanço nominal para compensar</p>
              </div>
              <span class="badge-count badge-success" id="badgeCol3Tag">Top Altas</span>
            </div>
            <div class="diag-lines-list" id="listLinhasEvolucao">
              <!-- Inserido dinamicamente via JS -->
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ====================================================================
         VISÃO 1: VISÃO GERAL & CARDS EXECUTIVOS
         ==================================================================== -->
    <section class="view-panel" id="view-geral">
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
      <!-- Filtros de Canal e Certificação GA4 Oficial -->
      <div class="filter-pills-bar" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div class="pill-group">
          <span style="font-weight: 700; font-size: 13px; text-transform: uppercase;">Canal Gráfico:</span>
          <button class="pill-btn active" data-traffic-ch="app">App</button>
          <button class="pill-btn" data-traffic-ch="site">Site</button>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="ga4-verified-badge" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 11.5px; font-weight: 700; background: rgba(16, 185, 129, 0.12); color: #059669; border: 1px solid rgba(16, 185, 129, 0.3);">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
            Google Analytics 4 Oficial (ID 340874176) — API Conectada &amp; Dados 100% Reais
          </span>
        </div>
      </div>

      <!-- Resumo de Indicadores Consolidados GA4 Oficial -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px;">
        <div class="hero-card" style="padding: 16px 18px;">
          <div style="font-size: 11.5px; color: var(--text-secondary); font-weight: 700; text-transform: uppercase;">Sessões Totais (GA4)</div>
          <div style="font-size: 24px; font-weight: 800; color: var(--text-primary); margin-top: 4px;">{tot_sessoes_ga:,}</div>
          <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px;">App: <strong>1.133.329</strong> | Site: <strong>1.440.896</strong></div>
        </div>
        <div class="hero-card" style="padding: 16px 18px;">
          <div style="font-size: 11.5px; color: var(--text-secondary); font-weight: 700; text-transform: uppercase;">Pedidos Rastreados (GA4)</div>
          <div style="font-size: 24px; font-weight: 800; color: var(--fsj-blue); margin-top: 4px;">{tot_pedidos_ga:,}</div>
          <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px;">App: <strong>112.462</strong> | Site: <strong>28.361</strong></div>
        </div>
        <div class="hero-card" style="padding: 16px 18px;">
          <div style="font-size: 11.5px; color: var(--text-secondary); font-weight: 700; text-transform: uppercase;">Taxa Média Conversão</div>
          <div style="font-size: 24px; font-weight: 800; color: #10b981; margin-top: 4px;">{tot_tx_conv_ga:.2f}%</div>
          <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px;">App: <strong style="color: #10b981;">9.92%</strong> | Site: <strong>1.97%</strong></div>
        </div>
        <div class="hero-card" style="padding: 16px 18px;">
          <div style="font-size: 11.5px; color: var(--text-secondary); font-weight: 700; text-transform: uppercase;">Receita Rastreada GA4</div>
          <div style="font-size: 24px; font-weight: 800; color: #0284c7; margin-top: 4px;">R$ {tot_receita_ga/1e6:.2f} Mi</div>
          <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px;">01 a {max_dia:02d}/09 (D-1 Oficial)</div>
        </div>
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
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
          <div>
            <h3 style="margin: 0; font-size: 16px; font-family: 'Outfit';">Desempenho por Origem de Tráfego / Canal de Mídia (GA4 Oficial)</h3>
            <span style="font-size: 11.5px; color: var(--text-secondary);">Propriedade Google Analytics: <strong>340874176</strong> | MTD 01 a {max_dia:02d}/09</span>
          </div>
          <span style="font-size: 11.5px; font-weight: 700; color: #059669; background: rgba(16, 185, 129, 0.1); padding: 4px 10px; border-radius: 6px;">
            ✓ 100% Dados Reais GA4
          </span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Origem / Mídia</th>
              <th>Canal</th>
              <th style="text-align: right;">Sessões</th>
              <th style="text-align: right;">Pedidos</th>
              <th style="text-align: right;">Tx. Conversão</th>
              <th style="text-align: right;">Receita (R$)</th>
              <th style="text-align: right;">Share</th>
            </tr>
          </thead>
          <tbody>
            {"".join([f'''<tr>
              <td style="font-weight: 700;">{o['origem']}</td>
              <td><span style="display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; background: var(--bg-card-subtle); color: var(--text-secondary);">{o['canal']}</span></td>
              <td style="text-align: right; font-weight: 600;">{o['sessoes']:,}</td>
              <td style="text-align: right;">{o['pedidos']:,}</td>
              <td style="text-align: right; font-weight: 700; color: {'#16a34a' if o['tx_conv']>=0.05 else '#2563eb'};">{o['tx_conv']*100:.2f}%</td>
              <td style="text-align: right; font-weight: 700;">R$ {o['receita']:,.2f}</td>
              <td style="text-align: right; color: var(--text-secondary);">{o['share']*100:.1f}%</td>
            </tr>''' for o in origens])}
          </tbody>
          <tfoot>
            <tr style="font-weight: 800; background: var(--bg-card-subtle); border-top: 2px solid var(--border-card);">
              <td>TOTAL CONSOLIDADO GA4</td>
              <td>Site + App</td>
              <td style="text-align: right; font-weight: 800;">{tot_sessoes_ga:,}</td>
              <td style="text-align: right; font-weight: 800;">{tot_pedidos_ga:,}</td>
              <td style="text-align: right; font-weight: 800; color: #16a34a;">{tot_tx_conv_ga:.2f}%</td>
              <td style="text-align: right; font-weight: 800; color: var(--fsj-blue);">R$ {tot_receita_ga:,.2f}</td>
              <td style="text-align: right; font-weight: 800;">100.0%</td>
            </tr>
          </tfoot>
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

    function switchView(targetViewId) {{
      navBtns.forEach(b => {{
        if (b.getAttribute('data-view') === targetViewId) {{
          b.classList.add('active');
        }} else {{
          b.classList.remove('active');
        }}
      }});

      viewPanels.forEach(p => {{
        if (p.id === targetViewId) {{
          p.classList.add('active');
        }} else {{
          p.classList.remove('active');
        }}
      }});

      if (targetViewId === 'view-anual') {{
        renderAnnualChart();
      }} else if (targetViewId === 'view-desvios') {{
        renderDesviosCharts(currentChannelV2);
      }} else if (targetViewId === 'view-trafego') {{
        renderTrafficCharts(currentTrafficCh);
      }}
    }}

    navBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        const targetViewId = btn.getAttribute('data-view');
        switchView(targetViewId);
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
      if (chartAnualInstance) renderAnnualChart();
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
    const maxDia = dashData.max_dia || 17;
    let selectedDiaIni = 1;
    let selectedDiaEnd = maxDia;
    let activeDatePreset = 'mtd';
    let isFigitalOn = localStorage.getItem('fsj_figital_included') === 'true';

    const inputDateIni = document.getElementById('filterDateIni');
    const inputDateEnd = document.getElementById('filterDateEnd');
    const datePeriodInfo = document.getElementById('datePeriodInfo');

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

    function calculateMetricsForRange(startDia, endDia) {{
      startDia = Math.max(1, Math.min(startDia, maxDia));
      endDia = Math.max(startDia, Math.min(endDia, maxDia));

      // Se for todo o MTD (1..maxDia), retorna direto kpis_mtd pré-calculado com precisão oficial
      if (startDia === 1 && endDia === maxDia && dashData.kpis_mtd) {{
        return JSON.parse(JSON.stringify(dashData.kpis_mtd));
      }}

      // Se for um único dia específico
      if (startDia === endDia && dashData.daily_history && dashData.daily_history[startDia]) {{
        return JSON.parse(JSON.stringify(dashData.daily_history[startDia]));
      }}

      // Se for um intervalo arbitrário entre startDia e endDia
      const channels = ['app', 'site', 'marketplace', 'televendas', 'figital', 'site_app', 'canais_digitais', 'ecommerce_total', 'ecossistema_total'];
      const res = {{}};

      channels.forEach(ch => {{
        let venda = 0;
        let venda_ant = 0;
        let venda_yoy = 0;
        let cupons = 0;
        let meta_mtd = 0;
        let cupons_meta_mtd = 0;
        let sessoes = 0;
        let sessoes_meta_mtd = 0;
        let rent_op_weighted = 0;
        let meta_mes = 0;
        let rent_op_meta = 20.0;
        let tx_conv_meta = 8.0;
        let tkm_meta = 120.0;

        for (let d = startDia; d <= endDia; d++) {{
          const dayObj = dashData.daily_history && dashData.daily_history[d] ? dashData.daily_history[d][ch] : null;
          if (dayObj) {{
            venda += (dayObj.venda || 0);
            venda_ant += (dayObj.venda_ant || 0);
            venda_yoy += (dayObj.venda_yoy || 0);
            cupons += (dayObj.cupons || 0);
            meta_mtd += (dayObj.meta_mtd || 0);
            cupons_meta_mtd += (dayObj.cupons_meta_mtd || 0);
            sessoes += (dayObj.sessoes || 0);
            sessoes_meta_mtd += (dayObj.sessoes_meta_mtd || 0);
            rent_op_weighted += (dayObj.rent_op || 0) * (dayObj.venda || 0);
            meta_mes = dayObj.meta_mes || meta_mes;
            rent_op_meta = dayObj.rent_op_meta || rent_op_meta;
            tx_conv_meta = dayObj.tx_conv_meta || tx_conv_meta;
            tkm_meta = dayObj.tkm_meta || tkm_meta;
          }}
        }}

        const tkm = cupons > 0 ? Number((venda / cupons).toFixed(2)) : 0;
        const rent_op = venda > 0 ? Number((rent_op_weighted / venda).toFixed(2)) : rent_op_meta;
        const rent_dre = Number((rent_op + 5.03).toFixed(2));
        const gap_venda_val = Number((venda - meta_mtd).toFixed(2));
        const desvio_venda_pct = meta_mtd > 0 ? Number((((venda / meta_mtd) - 1) * 100).toFixed(2)) : 0;
        const cupons_gap_val = cupons - cupons_meta_mtd;
        const cupons_desvio_pct = cupons_meta_mtd > 0 ? Number((((cupons / cupons_meta_mtd) - 1) * 100).toFixed(2)) : 0;
        const tkm_gap_val = Number((tkm - tkm_meta).toFixed(2));
        const tkm_desvio_pct = tkm_meta > 0 ? Number((((tkm / tkm_meta) - 1) * 100).toFixed(2)) : 0;
        const rent_op_desvio = Number((rent_op - rent_op_meta).toFixed(2));
        const cresc_mom = venda_ant > 0 ? Number((((venda / venda_ant) - 1) * 100).toFixed(2)) : 0;
        const evo_yoy = venda_yoy > 0 ? Number((((venda / venda_yoy) - 1) * 100).toFixed(2)) : 0;
        const tx_conv = sessoes > 0 ? Number(((cupons / sessoes) * 100).toFixed(2)) : 0;
        const tx_conv_desvio_pct = tx_conv_meta > 0 ? Number((((tx_conv / tx_conv_meta) - 1) * 100).toFixed(2)) : 0;
        const sessoes_gap_val = sessoes - sessoes_meta_mtd;
        const sessoes_desvio_pct = sessoes_meta_mtd > 0 ? Number((((sessoes / sessoes_meta_mtd) - 1) * 100).toFixed(2)) : 0;

        res[ch] = {{
          venda: Number(venda.toFixed(2)),
          venda_ant: Number(venda_ant.toFixed(2)),
          venda_yoy: Number(venda_yoy.toFixed(2)),
          cresc_mom: cresc_mom,
          evo_yoy: evo_yoy,
          cupons: cupons,
          tkm: tkm,
          rent_op: rent_op,
          rent_dre: rent_dre,
          sessoes: sessoes,
          tx_conv: tx_conv,
          meta_mtd: Number(meta_mtd.toFixed(2)),
          meta_mes: meta_mes,
          desvio_venda_pct: desvio_venda_pct,
          gap_venda_val: gap_venda_val,
          cupons_meta_mtd: cupons_meta_mtd,
          cupons_desvio_pct: cupons_desvio_pct,
          cupons_gap_val: cupons_gap_val,
          tkm_meta: tkm_meta,
          tkm_desvio_pct: tkm_desvio_pct,
          tkm_gap_val: tkm_gap_val,
          rent_op_meta: rent_op_meta,
          rent_op_desvio: rent_op_desvio,
          sessoes_meta_mtd: sessoes_meta_mtd,
          sessoes_desvio_pct: sessoes_desvio_pct,
          sessoes_gap_val: sessoes_gap_val,
          tx_conv_meta: tx_conv_meta,
          tx_conv_desvio_pct: tx_conv_desvio_pct,
          share_empresa: 0
        }};
      }});

      const totalDigitais = res['canais_digitais'] ? res['canais_digitais'].venda : 0;
      const totalEmpresaEst = totalDigitais / 0.129;
      channels.forEach(ch => {{
        if (res[ch] && totalEmpresaEst > 0) {{
          res[ch].share_empresa = Number(((res[ch].venda / totalEmpresaEst) * 100).toFixed(2));
        }}
      }});

      return res;
    }}

    function syncDateInputs() {{
      const pad = n => String(n).padStart(2, '0');
      if (inputDateIni) inputDateIni.value = `2026-09-${{pad(selectedDiaIni)}}`;
      if (inputDateEnd) inputDateEnd.value = `2026-09-${{pad(selectedDiaEnd)}}`;
    }}

    function updateDatePeriodBadge() {{
      if (!datePeriodInfo) return;
      const pad = n => String(n).padStart(2, '0');
      const numDias = (selectedDiaEnd - selectedDiaIni) + 1;
      if (selectedDiaIni === 1 && selectedDiaEnd === maxDia) {{
        datePeriodInfo.innerHTML = `<span>01 a ${{pad(maxDia)}}/09/2026 (${{maxDia}} dias MTD D-1)</span>`;
      }} else if (selectedDiaIni === selectedDiaEnd) {{
        datePeriodInfo.innerHTML = `<span>Dia ${{pad(selectedDiaIni)}}/09/2026 (Fechamento D-1)</span>`;
      }} else {{
        datePeriodInfo.innerHTML = `<span>${{pad(selectedDiaIni)}} a ${{pad(selectedDiaEnd)}}/09/2026 (${{numDias}} dias apurados)</span>`;
      }}
    }}

    function selectDatePreset(preset) {{
      activeDatePreset = preset;
      document.querySelectorAll('.preset-pill').forEach(pill => pill.classList.remove('active'));

      if (preset === 'mtd') {{
        selectedDiaIni = 1;
        selectedDiaEnd = maxDia;
        const pill = document.getElementById('presetMtd');
        if (pill) pill.classList.add('active');
      }} else if (preset === 'yesterday') {{
        selectedDiaIni = maxDia;
        selectedDiaEnd = maxDia;
        const pill = document.getElementById('presetYesterday');
        if (pill) pill.classList.add('active');
      }} else if (preset === '7days') {{
        selectedDiaIni = Math.max(1, maxDia - 6);
        selectedDiaEnd = maxDia;
        const pill = document.getElementById('preset7Days');
        if (pill) pill.classList.add('active');
      }} else if (preset === 'this_week') {{
        selectedDiaIni = Math.max(1, maxDia - ((new Date(2026, 8, maxDia).getDay() + 6) % 7));
        selectedDiaEnd = maxDia;
        const pill = document.getElementById('presetThisWeek');
        if (pill) pill.classList.add('active');
      }}

      syncDateInputs();
      updateDatePeriodBadge();
      updateDashboardState();
    }}

    function onDateInputChange() {{
      if (!inputDateIni || !inputDateEnd) return;
      const parseDia = val => {{
        if (!val) return null;
        const parts = val.split('-');
        return parts.length === 3 ? parseInt(parts[2], 10) : null;
      }};

      let dIni = parseDia(inputDateIni.value);
      let dEnd = parseDia(inputDateEnd.value);

      if (dIni === null || isNaN(dIni)) dIni = 1;
      if (dEnd === null || isNaN(dEnd)) dEnd = maxDia;

      dIni = Math.max(1, Math.min(dIni, maxDia));
      dEnd = Math.max(dIni, Math.min(dEnd, maxDia));

      selectedDiaIni = dIni;
      selectedDiaEnd = dEnd;

      document.querySelectorAll('.preset-pill').forEach(pill => pill.classList.remove('active'));
      if (selectedDiaIni === 1 && selectedDiaEnd === maxDia) {{
        activeDatePreset = 'mtd';
        const pill = document.getElementById('presetMtd');
        if (pill) pill.classList.add('active');
      }} else if (selectedDiaIni === maxDia && selectedDiaEnd === maxDia) {{
        activeDatePreset = 'yesterday';
        const pill = document.getElementById('presetYesterday');
        if (pill) pill.classList.add('active');
      }} else {{
        activeDatePreset = 'custom';
      }}

      syncDateInputs();
      updateDatePeriodBadge();
      updateDashboardState();
    }}

    function getMetricsForCurrentSelection() {{
      const baseMetrics = calculateMetricsForRange(selectedDiaIni, selectedDiaEnd);
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
          const diasRest = Math.max(1, 30 - selectedDiaEnd);
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
      if (typeof updateAnnualViewFigital === 'function') {{
        updateAnnualViewFigital(included);
      }}
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

    // Inicialização do Filtro de Data Apple
    syncDateInputs();
    updateDatePeriodBadge();

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

    // =========================================================================
    // VISÃO 0: VISÃO ANUAL 2026 & DIAGNÓSTICO DE INVOLUÇÕES
    // =========================================================================
    let selectedAnnualMonthKey = '2026-09';
    let chartAnualInstance = null;

    function initAnnualView() {{
      const vAnual = dashData.visao_anual;
      if (!vAnual || !vAnual.meses || vAnual.meses.length === 0) return;
      
      selectedAnnualMonthKey = vAnual.meses[vAnual.meses.length - 1].key;
      renderAnnualMonthPills();
      renderAnnualChart();
      selectAnnualMonth(selectedAnnualMonthKey);
    }}

    function renderAnnualMonthPills() {{
      const container = document.getElementById('annualMonthPills');
      if (!container || !dashData.visao_anual || !dashData.visao_anual.meses) return;
      const meses = dashData.visao_anual.meses;

      container.innerHTML = meses.map(m => {{
        const isActive = m.key === selectedAnnualMonthKey;
        const ating = isFigitalOn ? m.atingimento_total_com_figital_pct : m.atingimento_digitais_pct;
        const isSuccess = ating >= 100;
        const badgeClass = isSuccess ? 'badge-success' : 'badge-danger';
        return `<button class="month-pill ${{isActive ? 'active' : ''}}" data-month="${{m.key}}" onclick="selectAnnualMonth('${{m.key}}')">
          <span>${{m.label}}</span>
          <span class="pill-badge ${{badgeClass}}">${{ating.toFixed(1)}}%</span>
        </button>`;
      }}).join('');
    }}

    function renderAnnualChart() {{
      const ctx = document.getElementById('chartAnualMeses');
      if (!ctx || !dashData.visao_anual || !dashData.visao_anual.meses) return;
      const meses = dashData.visao_anual.meses;
      const labels = meses.map(m => m.label);

      if (chartAnualInstance) {{
        chartAnualInstance.destroy();
      }}

      let datasets = [];

      if (isFigitalOn) {{
        datasets = [
          {{
            type: 'bar',
            label: 'Canais Digitais (Site+App+MKP)',
            data: meses.map(m => Number((m.real_digitais / 1e6).toFixed(3))),
            backgroundColor: currentTheme === 'dark' ? '#38bdf8' : '#0077ff',
            borderRadius: {{ topLeft: 0, topRight: 0, bottomLeft: 6, bottomRight: 6 }},
            stack: 'vendas',
            order: 2,
            datalabels: {{ display: false }}
          }},
          {{
            type: 'bar',
            label: 'Figital',
            data: meses.map(m => Number(((m.real_figital || 0) / 1e6).toFixed(3))),
            backgroundColor: currentTheme === 'dark' ? '#c084fc' : '#8b5cf6',
            borderRadius: {{ topLeft: 6, topRight: 6, bottomLeft: 0, bottomRight: 0 }},
            stack: 'vendas',
            order: 2,
            datalabels: {{
              display: true,
              anchor: 'end',
              align: 'top',
              offset: 4,
              font: {{ size: 10, weight: '700' }},
              color: () => currentTheme === 'dark' ? '#f8fafc' : '#1e293b',
              formatter: (val, ctx) => {{
                const total = (meses[ctx.dataIndex].real_digitais + (meses[ctx.dataIndex].real_figital || 0)) / 1e6;
                return 'R$ ' + total.toFixed(1).replace('.', ',') + 'M';
              }}
            }}
          }},
          {{
            type: 'line',
            label: 'Meta Oficial (+ Figital)',
            data: meses.map(m => Number(((m.meta_total_com_figital || m.meta_digitais) / 1e6).toFixed(3))),
            borderColor: currentTheme === 'dark' ? '#fbbf24' : '#003875',
            backgroundColor: 'transparent',
            borderWidth: 2.8,
            borderDash: [6, 4],
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: currentTheme === 'dark' ? '#fbbf24' : '#003875',
            tension: 0.15,
            order: 1,
            datalabels: {{ display: false }}
          }}
        ];
      }} else {{
        datasets = [
          {{
            type: 'bar',
            label: 'Realizado Canais Digitais',
            data: meses.map(m => Number((m.real_digitais / 1e6).toFixed(3))),
            backgroundColor: meses.map(m => m.atingimento_digitais_pct >= 100 
              ? (currentTheme === 'dark' ? '#38bdf8' : '#0077ff') 
              : (currentTheme === 'dark' ? '#f87171' : '#ef4444')),
            borderRadius: 6,
            order: 2,
            datalabels: {{
              display: true,
              anchor: 'end',
              align: 'top',
              offset: 4,
              font: {{ size: 10, weight: '700' }},
              color: () => currentTheme === 'dark' ? '#f8fafc' : '#1e293b',
              formatter: val => 'R$ ' + val.toFixed(1).replace('.', ',') + 'M'
            }}
          }},
          {{
            type: 'line',
            label: 'Meta Oficial Digitais',
            data: meses.map(m => Number((m.meta_digitais / 1e6).toFixed(3))),
            borderColor: currentTheme === 'dark' ? '#fbbf24' : '#003875',
            backgroundColor: 'transparent',
            borderWidth: 2.8,
            borderDash: [6, 4],
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: currentTheme === 'dark' ? '#fbbf24' : '#003875',
            tension: 0.15,
            order: 1,
            datalabels: {{ display: false }}
          }}
        ];
      }}

      chartAnualInstance = new Chart(ctx.getContext('2d'), {{
        data: {{
          labels: labels,
          datasets: datasets
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 30, bottom: 12, left: 16, right: 16 }} }},
          interaction: {{
            mode: 'index',
            intersect: false
          }},
          onClick: (event, elements) => {{
            if (elements && elements.length > 0) {{
              const idx = elements[0].index;
              const m = meses[idx];
              if (m) {{
                selectAnnualMonth(m.key);
                const diagEl = document.getElementById('diagnosticPanel');
                if (diagEl) diagEl.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
              }}
            }}
          }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: R$ ${{ctx.raw.toFixed(2).replace('.', ',')}} Mi`,
                afterBody: (tooltipItems) => {{
                  if (tooltipItems.length === 0) return '';
                  const idx = tooltipItems[0].dataIndex;
                  const m = meses[idx];
                  const ating = isFigitalOn ? m.atingimento_total_com_figital_pct : m.atingimento_digitais_pct;
                  const gap = isFigitalOn ? m.desvio_total_com_figital_val : m.desvio_digitais_val;
                  const gapStr = (gap >= 0 ? '+R$ ' : '-R$ ') + (Math.abs(gap)/1e6).toFixed(2).replace('.', ',') + ' Mi';
                  return [
                    '--------------------------',
                    `Atingimento: ${{ating.toFixed(1).replace('.', ',')}}%`,
                    `Desvio: ${{gapStr}}`,
                    '👉 Clique para abrir diagnóstico'
                  ];
                }}
              }}
            }}
          }},
          scales: {{
            y: {{
              grid: {{ color: getGridColor() }},
              ticks: {{
                color: getTextColor(),
                callback: val => 'R$ ' + val + 'M'
              }}
            }},
            x: {{
              offset: true,
              grid: {{ display: false }},
              ticks: {{ color: getTextColor(), font: {{ weight: '700' }} }}
            }}
          }}
        }}
      }});
    }}

    let currentDiagMode = 'mom'; // 'mom' ou 'yoy'

    function setDiagComparisonMode(mode) {{
      currentDiagMode = mode;
      const btnMoM = document.getElementById('btnDiagMoM');
      const btnYoY = document.getElementById('btnDiagYoY');
      if (btnMoM && btnYoY) {{
        if (mode === 'mom') {{
          btnMoM.classList.add('active');
          btnYoY.classList.remove('active');
        }} else {{
          btnYoY.classList.add('active');
          btnMoM.classList.remove('active');
        }}
      }}
      selectAnnualMonth(selectedAnnualMonthKey);
    }}

    function selectAnnualMonth(monthKey) {{
      if (!dashData.visao_anual || !dashData.visao_anual.meses) return;
      selectedAnnualMonthKey = monthKey;
      const meses = dashData.visao_anual.meses;
      const m = meses.find(item => item.key === monthKey) || meses[meses.length - 1];

      // Atualiza pílulas do mês
      document.querySelectorAll('#annualMonthPills .month-pill').forEach(btn => {{
        if (btn.getAttribute('data-month') === monthKey) {{
          btn.classList.add('active');
        }} else {{
          btn.classList.remove('active');
        }}
      }});

      // Atualiza botões MoM / YoY
      const btnMoM = document.getElementById('btnDiagMoM');
      const btnYoY = document.getElementById('btnDiagYoY');
      if (btnMoM && btnYoY) {{
        if (currentDiagMode === 'mom') {{
          btnMoM.classList.add('active');
          btnYoY.classList.remove('active');
        }} else {{
          btnYoY.classList.add('active');
          btnMoM.classList.remove('active');
        }}
      }}

      // Dados de faturamento do mês
      const real = isFigitalOn ? (m.real_digitais + (m.real_figital || 0)) : m.real_digitais;
      const meta = isFigitalOn ? (m.meta_total_com_figital || m.meta_digitais) : m.meta_digitais;
      const desvioVal = real - meta;
      const desvioPct = meta > 0 ? ((real / meta) - 1) * 100 : 0;
      const atingPct = meta > 0 ? (real / meta) * 100 : 100;
      const isSuccess = atingPct >= 100;

      // Status Badge
      const statusBadge = document.getElementById('diagStatusBadge');
      if (statusBadge) {{
        if (isSuccess) {{
          statusBadge.className = 'diag-badge-pill';
          statusBadge.style.background = 'var(--badge-green-bg)';
          statusBadge.style.color = 'var(--badge-green-text)';
          statusBadge.textContent = '🟢 Meta Superada (' + atingPct.toFixed(1).replace('.', ',') + '%)';
        }} else {{
          statusBadge.className = 'diag-badge-pill';
          statusBadge.style.background = 'var(--badge-red-bg)';
          statusBadge.style.color = 'var(--badge-red-text)';
          statusBadge.textContent = '🔴 Abaixo da Meta (' + atingPct.toFixed(1).replace('.', ',') + '%)';
        }}
      }}

      // Título e Subtítulo
      const monthTitle = document.getElementById('diagMonthTitle');
      if (monthTitle) monthTitle.textContent = 'Diagnóstico Executivo — ' + m.nome_completo;

      const subTitle = document.getElementById('diagSubtitle');
      const noticeBox = document.getElementById('diagProrataNotice');
      const noticeText = document.getElementById('diagNoticeText');
      const metric4Lbl = document.getElementById('diagMetric4Lbl');
      const thColAnt = document.getElementById('thColAnt');
      const thColDelta = document.getElementById('thColDelta');
      const thColVar = document.getElementById('thColVar');
      const diagCol1Title = document.getElementById('diagCol1Title');
      const diagCol1Desc = document.getElementById('diagCol1Desc');
      const diagCol2Title = document.getElementById('diagCol2Title');
      const diagCol2Desc = document.getElementById('diagCol2Desc');
      const badgeCol2Tag = document.getElementById('badgeCol2Tag');
      const diagCol3Title = document.getElementById('diagCol3Title');
      const diagCol3Desc = document.getElementById('diagCol3Desc');
      const badgeCol3Tag = document.getElementById('badgeCol3Tag');

      const isSetembro = m.key === '2026-09';
      const maxD = dashData.max_dia || 17;

      const setEl = (id, val, cls) => {{
        const el = document.getElementById(id);
        if (el) {{
          el.textContent = val;
          if (cls !== undefined) el.className = 'val ' + cls;
        }}
      }};

      setEl('diagRealDigitais', fmtCurrency(real));
      setEl('diagMetaDigitais', fmtCurrency(meta));
      const gapSign = desvioVal >= 0 ? '+' : '';
      const gapCls = desvioVal >= 0 ? 'val-positive' : 'val-negative';
      setEl('diagDesvioDigitais', gapSign + fmtCurrency(desvioVal) + ' (' + fmtPctStr(desvioPct) + ')', gapCls);

      const diagData = m.diagnostico || {{}};

      if (currentDiagMode === 'mom') {{
        if (isSetembro) {{
          if (subTitle) subTitle.textContent = 'Setembro em andamento (' + maxD + ' dias apurados). Comparativo com ritmo diário equivalente de Agosto (' + maxD + 'd pró-rata) para eliminar distorções.';
          if (noticeBox) noticeBox.style.display = 'flex';
          if (noticeText) noticeText.innerHTML = `<strong>Base Normalizada Pró-rata:</strong> Para Setembro (${{maxD}} dias apurados), os comparativos MoM utilizam o ritmo diário equivalente de Agosto (${{maxD}} dias pró-rata: R$ 1,945 Mi/dia vs R$ 1,804 Mi/dia = +7,8%) para eliminar a falsa impressão de queda por mês incompleto.`;
          if (metric4Lbl) metric4Lbl.textContent = 'Ritmo Diário MoM';
          setEl('diagMoM', 'R$ 1,945 Mi/dia (+7,8%)', 'val-positive');
        }} else {{
          if (subTitle) subTitle.textContent = 'Comparativo de desempenho vs mês anterior e detalhamento das categorias e linhas em evolução e involução.';
          if (noticeBox) noticeBox.style.display = 'none';
          if (metric4Lbl) metric4Lbl.textContent = 'Variação MoM';
          if (m.key === '2026-01') {{
            setEl('diagMoM', 'Mês Base 2026', '');
          }} else {{
            const momSign = m.mom_digitais_pct >= 0 ? '⇑ +' : '⇓ ';
            const momCls = m.mom_digitais_pct >= 0 ? 'val-positive' : 'val-negative';
            setEl('diagMoM', momSign + Math.abs(m.mom_digitais_pct).toFixed(1).replace('.', ',') + '%', momCls);
          }}
        }}

        setEl('diagYoY', '+60,9% vs 2025', 'val-positive');

        if (diagCol1Title) diagCol1Title.textContent = 'Categorias & Grupos';
        if (diagCol1Desc) diagCol1Desc.textContent = isSetembro ? 'Variação vs ritmo diário anterior normalizado (pró-rata 17d)' : 'Ordenadas pelas maiores variações vs mês anterior';
        if (thColAnt) thColAnt.textContent = isSetembro ? 'Mês Ant (Pró-rata)' : 'Mês Anterior';
        if (thColDelta) thColDelta.textContent = 'Delta (R$)';
        if (thColVar) thColVar.textContent = 'Var %';

        if (diagCol2Title) diagCol2Title.textContent = '⚠️ Linhas com Maior Queda (Ofensores)';
        if (diagCol2Desc) diagCol2Desc.textContent = 'Produtos/Linhas que mais puxaram o faturamento para baixo no período';
        if (badgeCol2Tag) badgeCol2Tag.textContent = 'Top Quedas';

        if (diagCol3Title) diagCol3Title.textContent = '🚀 Linhas com Maior Crescimento (Alavancas)';
        if (diagCol3Desc) diagCol3Desc.textContent = 'Produtos/Linhas com maior avanço nominal para compensar';
        if (badgeCol3Tag) badgeCol3Tag.textContent = 'Top Altas';

      }} else {{
        // Modo YoY
        if (subTitle) subTitle.textContent = 'Comparativo estrutural de evolução anual (YoY) em relação ao mesmo período de 2025.';
        if (noticeBox) noticeBox.style.display = 'flex';
        if (noticeText) noticeText.innerHTML = `<strong>Evolução Anual (YoY):</strong> Comparação direta com o mesmo período de 2025 (+60,9% de expansão digital) para mensurar ganho de escala e tração por categoria.`;
        if (metric4Lbl) metric4Lbl.textContent = 'Evolução YoY';
        setEl('diagMoM', '+60,9% vs Set/25', 'val-positive');
        setEl('diagYoY', 'Base 2025: R$ 20,54 Mi', '');

        if (diagCol1Title) diagCol1Title.textContent = 'Evolução Anual por Categoria (YoY)';
        if (diagCol1Desc) diagCol1Desc.textContent = 'Avanço nominal e percentual sobre o mesmo período de 2025';
        if (thColAnt) thColAnt.textContent = 'Ano Ant (2025)';
        if (thColDelta) thColDelta.textContent = 'Delta YoY (R$)';
        if (thColVar) thColVar.textContent = 'Evol %';

        if (diagCol2Title) diagCol2Title.textContent = '⚠️ Menor Evolução / Involução YoY';
        if (diagCol2Desc) diagCol2Desc.textContent = 'Linhas com recuo ou crescimento abaixo da média da empresa';
        if (badgeCol2Tag) badgeCol2Tag.textContent = 'Menor Tração';

        if (diagCol3Title) diagCol3Title.textContent = '🚀 Maiores Alavancas YoY (Expansão)';
        if (diagCol3Desc) diagCol3Desc.textContent = 'Linhas com maior volume incremental sobre 2025';
        if (badgeCol3Tag) badgeCol3Tag.textContent = 'Top Expansão';
      }}

      // 1. Tabela de Grupos / Categorias
      const tbodyGrupos = document.getElementById('tbodyGruposDiag');
      const countGrupos = document.getElementById('countGrupos');
      const grupos = (currentDiagMode === 'yoy' && diagData.grupos_yoy) ? diagData.grupos_yoy : (diagData.grupos || []);

      if (!grupos || grupos.length === 0) {{
        if (tbodyGrupos) {{
          tbodyGrupos.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-secondary); padding: 28px;">
            Janeiro é o mês inicial de referência (sem histórico anterior para cálculo de variação).
          </td></tr>`;
        }}
        if (countGrupos) countGrupos.textContent = 'Mês Inicial';
      }} else {{
        if (countGrupos) countGrupos.textContent = grupos.length + ' Categorias';
        if (tbodyGrupos) {{
          tbodyGrupos.innerHTML = grupos.map(g => {{
            const isDrop = g.delta_val < 0;
            const cls = isDrop ? 'val-negative' : 'val-positive';
            const arrow = isDrop ? '⇓' : '⇑';
            return `<tr>
              <td style="font-weight: 700;">${{g.grupo}}</td>
              <td style="text-align: right; font-weight: 700;">${{fmtCurrency(g.venda_mes)}}</td>
              <td style="text-align: right; color: var(--text-secondary);">${{fmtCurrency(g.venda_ant)}}</td>
              <td style="text-align: right;" class="${{cls}}"><strong>${{fmtGapVal(g.delta_val)}}</strong></td>
              <td style="text-align: right;" class="${{cls}}"><strong>${{arrow}} ${{Math.abs(g.delta_pct).toFixed(1).replace('.', ',')}}%</strong></td>
            </tr>`;
          }}).join('');
        }}
      }}

      // 2. Coluna Top Linhas em Involução / Menor Tração
      const listInv = document.getElementById('listLinhasInvolucao');
      const linhasInv = (currentDiagMode === 'yoy' && diagData.top_involucao_linhas_yoy) ? diagData.top_involucao_linhas_yoy : (diagData.top_involucao_linhas || []);
      if (listInv) {{
        if (!linhasInv || linhasInv.length === 0) {{
          listInv.innerHTML = `<div style="text-align: center; color: var(--text-secondary); padding: 24px;">
            Nenhuma involução de linha registrada neste mês.
          </div>`;
        }} else {{
          listInv.innerHTML = linhasInv.map(l => {{
            const isDrop = l.delta_val < 0;
            const cls = isDrop ? 'val-negative' : 'val-positive';
            const arrow = isDrop ? '⇓' : '⇑';
            const antLbl = currentDiagMode === 'yoy' ? '2025' : 'Ant';
            return `<div class="line-card-item">
              <div class="line-info-left">
                <span class="line-name">${{l.linha}}</span>
                <div class="line-meta">
                  <span class="line-grp-tag">${{l.grupo}}</span>
                  <span>Mês: <strong>${{fmtCurrency(l.venda_mes)}}</strong></span>
                  <span>(${{antLbl}}: ${{fmtCurrency(l.venda_ant)}})</span>
                </div>
              </div>
              <div class="line-delta-pill">
                <span class="val ${{cls}}">${{fmtGapVal(l.delta_val)}}</span>
                <span class="pct ${{cls}}">${{arrow}} ${{Math.abs(l.delta_pct).toFixed(1).replace('.', ',')}}%</span>
              </div>
            </div>`;
          }}).join('');
        }}
      }}

      // 3. Coluna Top Linhas em Evolução / Alavancas
      const listEvo = document.getElementById('listLinhasEvolucao');
      const linhasEvo = (currentDiagMode === 'yoy' && diagData.top_evolucao_linhas_yoy) ? diagData.top_evolucao_linhas_yoy : (diagData.top_evolucao_linhas || []);
      if (listEvo) {{
        if (!linhasEvo || linhasEvo.length === 0) {{
          listEvo.innerHTML = `<div style="text-align: center; color: var(--text-secondary); padding: 24px;">
            Nenhum crescimento expressivo de linhas registrado neste mês.
          </div>`;
        }} else {{
          listEvo.innerHTML = linhasEvo.map(l => {{
            const isDrop = l.delta_val < 0;
            const cls = isDrop ? 'val-negative' : 'val-positive';
            const arrow = isDrop ? '⇓' : '⇑';
            const antLbl = currentDiagMode === 'yoy' ? '2025' : 'Ant';
            return `<div class="line-card-item">
              <div class="line-info-left">
                <span class="line-name">${{l.linha}}</span>
                <div class="line-meta">
                  <span class="line-grp-tag">${{l.grupo}}</span>
                  <span>Mês: <strong>${{fmtCurrency(l.venda_mes)}}</strong></span>
                  <span>(${{antLbl}}: ${{fmtCurrency(l.venda_ant)}})</span>
                </div>
              </div>
              <div class="line-delta-pill">
                <span class="val ${{cls}}">${{fmtGapVal(l.delta_val)}}</span>
                <span class="pct ${{cls}}">${{arrow}} +${{Math.abs(l.delta_pct).toFixed(1).replace('.', ',')}}%</span>
              </div>
            </div>`;
          }}).join('');
        }}
      }}
    }}

    function updateAnnualViewFigital(included) {{
      if (!dashData.visao_anual || !dashData.visao_anual.ytd) return;
      const ytd = dashData.visao_anual.ytd;

      // Badges
      const digFig = document.getElementById('ytdDigFigitalBadge');
      const ecomFig = document.getElementById('ytdEcomFigitalBadge');
      const legendFig = document.getElementById('annualLegendFigital');
      if (digFig) digFig.style.display = included ? 'inline-flex' : 'none';
      if (ecomFig) ecomFig.style.display = included ? 'inline-flex' : 'none';
      if (legendFig) legendFig.style.display = included ? 'inline-flex' : 'none';

      // YTD Card E-Commerce
      const ecomData = included ? ytd.ecommerce_com_figital : ytd.ecommerce_sem_figital;
      if (ecomData) {{
        const setT = (id, val) => {{ const el = document.getElementById(id); if (el) el.textContent = val; }};
        setT('ytdEcomReal', fmtCurrency(ecomData.real));
        setT('ytdEcomMeta', fmtCurrency(ecomData.meta));
        setT('ytdEcomDesvioVal', fmtGapVal(ecomData.desvio_val));
        setT('ytdEcomDesvioPct', fmtPctStr(ecomData.desvio_pct));
        setT('ytdEcomAting', ecomData.atingimento_pct.toFixed(1).replace('.', ',') + '% Meta');

        const desvValEl = document.getElementById('ytdEcomDesvioVal');
        const desvPctEl = document.getElementById('ytdEcomDesvioPct');
        const cls = ecomData.desvio_val >= 0 ? 'val-positive' : 'val-negative';
        if (desvValEl) desvValEl.className = 'val ' + cls;
        if (desvPctEl) desvPctEl.className = 'val ' + cls;
      }}

      // YTD Card Digitais
      if (ytd.digitais) {{
        const digReal = included ? (ytd.digitais.real + (ytd.ecommerce_com_figital.real - ytd.ecommerce_sem_figital.real)) : ytd.digitais.real;
        const digMeta = included ? (ytd.digitais.meta + (ytd.ecommerce_com_figital.meta - ytd.ecommerce_sem_figital.meta)) : ytd.digitais.meta;
        const digDesvVal = digReal - digMeta;
        const digDesvPct = digMeta > 0 ? ((digReal / digMeta) - 1) * 100 : 0;
        const digAting = digMeta > 0 ? (digReal / digMeta) * 100 : 100;

        const setT = (id, val) => {{ const el = document.getElementById(id); if (el) el.textContent = val; }};
        setT('ytdDigReal', fmtCurrency(digReal));
        setT('ytdDigMeta', fmtCurrency(digMeta));
        setT('ytdDigDesvioVal', fmtGapVal(digDesvVal));
        setT('ytdDigDesvioPct', fmtPctStr(digDesvPct));
        setT('ytdDigAting', digAting.toFixed(1).replace('.', ',') + '% Meta');

        const desvValEl = document.getElementById('ytdDigDesvioVal');
        const desvPctEl = document.getElementById('ytdDigDesvioPct');
        const cls = digDesvVal >= 0 ? 'val-positive' : 'val-negative';
        if (desvValEl) desvValEl.className = 'val ' + cls;
        if (desvPctEl) desvPctEl.className = 'val ' + cls;
      }}

      // Card 4 Projeção Anual Ponderada Q4 (Black Friday + Natal)
      const projAnoVal = document.getElementById('projAnoVal');
      const projSubtitle = document.getElementById('projSubtitle');
      const projBadge = document.getElementById('projBadge');
      const projDesc = document.getElementById('projDesc');
      const projMetaAno = document.getElementById('projMetaAno');
      const projSuperacao = document.getElementById('projSuperacao');

      if (included) {{
        if (projAnoVal) projAnoVal.textContent = '~R$ 728 Mi';
        if (projSubtitle) projSubtitle.textContent = 'Canais Digitais + Figital (Omnichannel)';
        if (projBadge) {{
          projBadge.textContent = '+ Figital Integrado';
          projBadge.style.background = 'var(--badge-purple-bg)';
          projBadge.style.color = 'var(--badge-purple-text)';
        }}
        if (projDesc) projDesc.textContent = 'Expectativa Consolidada com Q4 Acelerado + Lojas Físicas';
        if (projMetaAno) projMetaAno.textContent = 'R$ 715.0 Mi';
        if (projSuperacao) projSuperacao.textContent = '+R$ 13.0 Mi (+1.8%)';
      }} else {{
        if (projAnoVal) projAnoVal.textContent = '~R$ 688 Mi';
        if (projSubtitle) projSubtitle.textContent = 'Modelo Ponderado com Sazonalidade Q4';
        if (projBadge) {{
          projBadge.textContent = 'Sazonal Q4 (BF + Natal)';
          projBadge.style.background = '#fef3c7';
          projBadge.style.color = '#b45309';
        }}
        if (projDesc) projDesc.textContent = 'Expectativa Consolidada com Q4 Acelerado';
        if (projMetaAno) projMetaAno.textContent = 'R$ 683.0 Mi';
        if (projSuperacao) projSuperacao.textContent = '+R$ 5.0 Mi (+0.7%)';
      }}

      // Atualiza pílulas e re-renderiza gráfico e diagnóstico
      renderAnnualMonthPills();
      renderAnnualChart();
      selectAnnualMonth(selectedAnnualMonthKey);
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
              suggestedMin: 15,
              suggestedMax: 32,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return val + '%'; }}
              }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
              suggestedMin: -4,
              suggestedMax: 4,
              ticks: {{
                color: getTextColor(),
                callback: function(val) {{ return (val > 0 ? '+' : '') + val + '%'; }}
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
    initAnnualView();
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
