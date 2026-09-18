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
        return f"R$ {val/1e6:.3f}".replace('.', ',') + " Mi"
    elif abs(val) >= 1e3:
        return f"R$ {val/1e3:.1f}".replace('.', ',') + " K"
    return f"R$ {int(round(val)):,}".replace(',', '.')

def fmt_gap(val):
    sign = "+" if val >= 0 else "-"
    abs_val = abs(val)
    if abs_val >= 1e6:
        return f"{sign}R$ {abs_val/1e6:.3f}".replace('.', ',') + " Mi"
    elif abs_val >= 1e3:
        return f"{sign}R$ {abs_val/1e3:.1f}".replace('.', ',') + " K"
    return f"{sign}R$ {int(round(abs_val)):,}".replace(',', '.')

def fmt_pct(val):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%".replace('.', ',')

def fmt_growth(val):
    if val >= 0:
        return f"⇑ +{val:.1f}%".replace('.', ',')
    return f"⇓ -{abs(val):.1f}%".replace('.', ',')

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

    # Precomputações Visão 1 — Storytelling Executivo (Cards Diários/MTD)
    k_dig = kpis.get('canais_digitais', {})
    k_ecom = kpis.get('ecommerce_total', {})
    k_app = kpis.get('app', {})
    k_mkp = kpis.get('marketplace', {})
    k_site = kpis.get('site', {})
    k_fig = kpis.get('figital', {})
    p_dig = proj.get('canais_digitais', {})

    card1_venda_str = fmt_curr(k_dig.get('venda', 0))
    card1_meta_mtd_str = fmt_curr(k_dig.get('meta_mtd', 0))
    card1_meta_mes_str = f"R$ {k_dig.get('meta_mes', 0)/1e6:.3f}".replace('.', ',') + " Mi"
    card1_gap_val_str = fmt_gap(k_dig.get('gap_venda_val', 0))
    card1_desvio_pct_str = fmt_pct(k_dig.get('desvio_venda_pct', 0))
    card1_desv_cls = 'val-positive' if k_dig.get('gap_venda_val', 0) >= 0 else 'val-negative'
    card1_banner_cls = 'hero-gap-banner' if k_dig.get('gap_venda_val', 0) >= 0 else 'hero-gap-banner negative'
    card1_ating_mes_pct = (k_dig.get('venda', 0) / k_dig.get('meta_mes', 1) * 100) if k_dig.get('meta_mes', 0) > 0 else 0
    card1_prog_cls = 'mini-progress-fill over-target' if card1_ating_mes_pct >= (max_dia / 30 * 100) else 'mini-progress-fill'

    app_venda_str = fmt_curr(k_app.get('venda', 0))
    app_share_str = f"{k_app.get('share_empresa', 0):.2f}%".replace('.', ',')
    app_desv_str = fmt_pct(k_app.get('desvio_venda_pct', 0))
    app_gap_str = fmt_gap(k_app.get('gap_venda_val', 0))
    app_badge_cls = 'badge-driver-pos' if k_app.get('gap_venda_val', 0) >= 0 else 'badge-driver-neg'

    mkp_venda_str = fmt_curr(k_mkp.get('venda', 0))
    mkp_share_str = f"{k_mkp.get('share_empresa', 0):.2f}%".replace('.', ',')
    mkp_desv_str = fmt_pct(k_mkp.get('desvio_venda_pct', 0))
    mkp_gap_str = fmt_gap(k_mkp.get('gap_venda_val', 0))
    mkp_badge_cls = 'badge-driver-pos' if k_mkp.get('gap_venda_val', 0) >= 0 else 'badge-driver-neg'

    site_venda_str = fmt_curr(k_site.get('venda', 0))
    site_share_str = f"{k_site.get('share_empresa', 0):.2f}%".replace('.', ',')
    site_desv_str = fmt_pct(k_site.get('desvio_venda_pct', 0))
    site_gap_str = fmt_gap(k_site.get('gap_venda_val', 0))
    site_badge_cls = 'badge-driver-pos' if k_site.get('gap_venda_val', 0) >= 0 else 'badge-driver-neg'

    fig_venda_str = fmt_curr(k_fig.get('venda', 0))
    fig_share_str = f"{k_fig.get('share_empresa', 0):.2f}%".replace('.', ',')
    fig_desv_str = fmt_pct(k_fig.get('desvio_venda_pct', 0))
    fig_gap_str = fmt_gap(k_fig.get('gap_venda_val', 0))
    fig_badge_cls = 'badge-driver-pos' if k_fig.get('gap_venda_val', 0) >= 0 else 'badge-driver-neg'

    tkm_real_str = f"R$ {k_dig.get('tkm', 0):.2f}".replace('.', ',')
    tkm_meta_str = f"R$ {k_dig.get('tkm_meta', 0):.2f}".replace('.', ',')
    tkm_gap_str = fmt_gap(k_dig.get('tkm_gap_val', 0))
    tkm_desv_str = fmt_pct(k_dig.get('tkm_desvio_pct', 0))
    tkm_cls = 'val-positive' if k_dig.get('tkm_gap_val', 0) >= 0 else 'val-negative'

    rent_op_str = f"{k_dig.get('rent_op', 0):.2f}%".replace('.', ',')
    rent_meta_str = f"{k_dig.get('rent_op_meta', 0):.2f}%".replace('.', ',')
    rent_dre_str = f"{k_dig.get('rent_dre', 0):.2f}%".replace('.', ',')
    rent_cls = 'val-positive' if k_dig.get('rent_op_desvio', 0) >= 0 else 'val-negative'

    cupons_str = f"{k_dig.get('cupons', 0)/1e3:.2f}".replace('.', ',') + " Mil" if k_dig.get('cupons', 0) >= 1e3 else str(k_dig.get('cupons', 0))
    cupons_desv_str = fmt_pct(k_dig.get('cupons_desvio_pct', 0))
    cupons_cls = 'val-positive' if k_dig.get('cupons_desvio_pct', 0) >= 0 else 'val-negative'
    evo_yoy_str = fmt_growth(k_dig.get('evo_yoy', 0))

    diaria_nec_str = f"R$ {p_dig.get('venda_diaria_necessaria', 0)/1e3:.0f}".replace('.', ',') + " K/dia"
    run_rate_str = f"R$ {p_dig.get('run_rate_diario_atual', 0)/1e3:.0f}".replace('.', ',') + " K/dia"
    meta_rest_str = fmt_curr(p_dig.get('meta_restante', 0))
    fechamento_str = fmt_curr(p_dig.get('fechamento_projetado', 0))
    ating_proj_str = f"{p_dig.get('atingimento_projetado_pct', 100.0):.1f}%".replace('.', ',')
    gap_fech_str = fmt_gap(p_dig.get('gap_fechamento_val', 0))
    proj_pos_cls = 'val-positive' if p_dig.get('gap_fechamento_val', 0) >= 0 else 'val-negative'

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
       NOVO DESIGN SYSTEM EXECUTIVO: CARDS DE STORYTELLING (PIRÂMIDE DE MINTO)
       ========================================================================== */
    .hero-gap-banner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      border-radius: var(--radius-md);
      background: var(--badge-green-bg);
      color: var(--badge-green-text);
      font-size: 12px;
      font-weight: 700;
      transition: var(--transition);
    }}

    .hero-gap-banner.negative {{
      background: var(--badge-red-bg);
      color: var(--badge-red-text);
    }}

    .hero-gap-banner .gap-highlight {{
      font-size: 13.5px;
      font-weight: 800;
      letter-spacing: -0.2px;
    }}

    /* Barra de Progresso Mensal em Miniatura */
    .month-progress-box {{
      display: flex;
      flex-direction: column;
      gap: 5px;
      margin-top: 2px;
    }}

    .month-progress-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .month-progress-labels strong {{
      color: var(--text-primary);
    }}

    .mini-progress-track {{
      height: 7px;
      width: 100%;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      border-radius: 99px;
      overflow: hidden;
      position: relative;
    }}

    .mini-progress-fill {{
      height: 100%;
      border-radius: 99px;
      background: var(--fsj-blue-gradient);
      transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .mini-progress-fill.over-target {{
      background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
    }}

    /* Driver Rows (Card 2: Motores de Crescimento) */
    .driver-rows-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .driver-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 10px;
      border-radius: var(--radius-md);
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      font-size: 12px;
      transition: var(--transition);
    }}

    .driver-item:hover {{
      background: var(--bg-card-hover);
      border-color: rgba(0, 119, 255, 0.25);
    }}

    .driver-info-group {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .driver-name {{
      font-weight: 800;
      font-size: 12px;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .driver-share-tag {{
      font-size: 10px;
      font-weight: 600;
      color: var(--text-secondary);
      background: var(--bg-card);
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid var(--border-card);
    }}

    .driver-metrics-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      text-align: right;
    }}

    .driver-sales-val {{
      font-weight: 700;
      color: var(--text-primary);
      font-size: 12px;
    }}

    .driver-badge-desv {{
      font-size: 10.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: var(--radius-pill);
    }}

    .badge-driver-pos {{
      background: rgba(34, 197, 94, 0.15);
      color: #16a34a;
    }}

    .badge-driver-neg {{
      background: rgba(239, 68, 68, 0.15);
      color: #dc2626;
    }}

    /* Grid 2x2 de Eficiência (Card 3) */
    .efficiency-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .efficiency-box {{
      padding: 8px 10px;
      border-radius: var(--radius-md);
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .efficiency-box .eff-lbl {{
      font-size: 10.5px;
      color: var(--text-secondary);
      font-weight: 600;
    }}

    .efficiency-box .eff-val {{
      font-size: 14.5px;
      font-weight: 800;
      color: var(--text-primary);
      font-family: 'Outfit', sans-serif;
    }}

    .efficiency-box .eff-sub {{
      font-size: 10px;
      font-weight: 600;
    }}

    /* Run Rate Grid (Card 4) */
    .runrate-grid {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .runrate-subrow {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 10px;
      border-radius: var(--radius-md);
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      font-size: 11.5px;
    }}

    .runrate-subrow strong {{
      color: var(--text-primary);
    }}

    /* Action Insight Footer no final de cada Card */
    .card-insight-footer {{
      border-top: 1px solid var(--border-card);
      padding-top: 8px;
      margin-top: auto;
      font-size: 11px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 6px;
      line-height: 1.35;
    }}

    .card-insight-footer strong {{
      color: var(--text-primary);
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

    /* Card do Gráfico Anual Completo */
    .card-chart-full {{
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-card);
      padding: 20px 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .card-chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .card-chart-header h3 {{
      font-family: 'Outfit', sans-serif;
      font-size: 17px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }}

    .card-chart-header p {{
      font-size: 12.5px;
      color: var(--text-secondary);
      max-width: 780px;
    }}

    .chart-legend-box {{
      display: inline-flex;
      align-items: center;
      gap: 14px;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-pill);
      padding: 6px 14px;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-color {{
      display: inline-block;
      width: 14px;
      height: 10px;
      border-radius: 3px;
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

      <!-- 4 Hero Cards Anuais (YTD) — Nova Arquitetura de Storytelling Anual -->
      <div class="top-hero-grid">
        <!-- Card 1: Faturamento Acumulado YTD -->
        <div class="hero-card highlight-card" id="cardAnualDigital">
          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3>Acumulado YTD (2026)</h3>
                <span class="badge-figital-pill" id="ytdDigFigitalBadge" style="display: none;">+ Figital</span>
              </div>
              <span class="hero-subtitle">Canais Digitais Acumulado (Jan a Set)</span>
            </div>
            <span class="hero-part-badge" style="background: var(--badge-green-bg); color: var(--badge-green-text);" id="ytdDigAting">
              {ytd_dig_ating_str}
            </span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" id="ytdDigReal">{ytd_dig_real_str}</span>
            <span class="hero-meta-mes">Meta YTD: <strong id="ytdDigMeta">{ytd_dig_meta_str}</strong></span>
          </div>
          <div class="hero-gap-banner {'' if ytd_dig.get('desvio_val', 0) >= 0 else 'negative'}" id="ytdDigGapBanner">
            <span>GAP R$: <strong class="gap-highlight" id="ytdDigDesvioVal">{ytd_dig_desvio_val_str}</strong></span>
            <span>Desvio: <strong id="ytdDigDesvioPct">{ytd_dig_desvio_pct_str}</strong></span>
          </div>
          <div class="card-insight-footer">
            <span>🟢</span> <span>Operação digital rodando no ritmo oficial do orçamento anual</span>
          </div>
        </div>

        <!-- Card 2: Balanço de Metas -->
        <div class="hero-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Balanço de Metas</h3>
              <span class="hero-subtitle">Consistência Mensal em 2026</span>
            </div>
            <span class="hero-part-badge" style="background: #e0f2fe; color: #0284c7;">55.6% Sucesso</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val" style="color: var(--badge-green-text);">5 Meses Batidos</span>
            <span class="hero-meta-mes">4 meses em recuperação (Abr-Jul)</span>
          </div>
          <div class="hero-gap-banner" style="background: rgba(0, 119, 255, 0.08); color: var(--fsj-blue);">
            <span>Melhor: <strong class="val-positive">Fev/26 (+109.5%)</strong></span>
            <span>Recorde: <strong style="color: var(--fsj-blue-light);">Ago/26 (R$ 55.9M)</strong></span>
          </div>
          <div class="card-insight-footer">
            <span>📅</span> <span>Média de <strong>R$ 51.7 Mi/mês</strong> com aceleração em Ago e Set</span>
          </div>
        </div>

        <!-- Card 3: Crescimento Anual (YoY vs 2025) -->
        <div class="hero-card">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Crescimento Anual (YoY)</h3>
              <span class="hero-subtitle">Ganho de Escala vs Jan-Set/2025</span>
            </div>
            <span class="hero-part-badge" style="background: var(--badge-green-bg); color: var(--badge-green-text);">⇑ +43.8% YoY</span>
          </div>
          <div class="hero-val-group">
            <span class="hero-main-val val-positive">+R$ 135.7 Mi</span>
            <span class="hero-meta-mes">Base 2025: <strong>R$ 309.9 Mi</strong></span>
          </div>
          <div class="hero-gap-banner" style="background: rgba(34, 197, 94, 0.08); color: #16a34a;">
            <span>Ritmo Set/26: <strong>R$ 1,945 Mi/dia</strong></span>
            <span>YoY Setembro: <strong class="val-positive">+60.9%</strong></span>
          </div>
          <div class="card-insight-footer">
            <span>🚀</span> <span>Forte ganho de escala alavancado pelo App e ecossistema</span>
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
            <span class="hero-meta-mes" id="projDesc">Expectativa com Q4 Acelerado</span>
          </div>
          <div class="hero-gap-banner" style="background: rgba(34, 197, 94, 0.1); color: #16a34a;">
            <span>Meta Anual: <strong id="projMetaAno">R$ 683.0 Mi</strong></span>
            <span>Superação: <strong class="val-positive" id="projSuperacao">+R$ 5.0 Mi (+0.7%)</strong></span>
          </div>
          <div class="card-insight-footer">
            <span>🎯</span> <span>Black Friday (Nov: R$ 80M) e Natal definirão o fechamento</span>
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
            <div class="legend-item"><span class="legend-color" id="legendColorReal" style="background: #0077ff;"></span> <span id="legendTextReal">Realizado Digital</span></div>
            <div class="legend-item"><span class="legend-color" id="legendColorMeta" style="background: #003875; border-top: 2px dashed #003875;"></span> <span id="legendTextMeta">Meta Oficial</span></div>
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
         VISÃO 1: ACOMPANHAMENTO DIÁRIO & MTD (VISÃO GERAL)
         ==================================================================== -->
    <section class="view-panel" id="view-geral">
      <!-- 4 Top Hero Cards — Nova Arquitetura de Storytelling Executivo -->
      <div class="top-hero-grid">
        <!-- Card 1: Faturamento Consolidado (O Grande Veredito) -->
        <div class="hero-card highlight-card" id="cardConsolidado">
          <div class="hero-header">
            <div class="hero-title-group">
              <div style="display: flex; align-items: center; gap: 6px;">
                <h3 id="consTitle">Canais Digitais</h3>
                <span class="badge-figital-pill" id="consFigitalBadge" style="display: none;">+ Figital</span>
              </div>
              <span class="hero-subtitle" id="consSubtitle">Venda Efetiva no Período</span>
            </div>
            <span class="hero-part-badge" id="consPartBadge">Part: {k_dig.get('share_empresa', 0):.2f}%</span>
          </div>

          <div class="hero-val-group">
            <span class="hero-main-val" id="consMainVal">{card1_venda_str}</span>
            <span class="hero-meta-mes">Meta Proporcional: <strong id="consMetaMTD">{card1_meta_mtd_str}</strong></span>
          </div>

          <div class="{card1_banner_cls}" id="consGapBanner">
            <span>GAP R$: <strong class="gap-highlight" id="consGapVal">{card1_gap_val_str}</strong></span>
            <span>Desvio: <strong id="consDesvioPct">{card1_desvio_pct_str}</strong></span>
          </div>

          <div class="month-progress-box">
            <div class="month-progress-labels">
              <span>Progresso Meta Mês: <strong id="consProgPct">{card1_ating_mes_pct:.1f}%</strong></span>
              <span id="consMetaMes">Meta: {card1_meta_mes_str}</span>
            </div>
            <div class="mini-progress-track">
              <div class="{card1_prog_cls}" id="consProgFill" style="width: {min(100, card1_ating_mes_pct):.1f}%;"></div>
            </div>
          </div>

          <div class="card-insight-footer" id="consInsight">
            <span>💡</span> <span id="consInsightTxt">Superando a meta proporcional em <strong>{card1_gap_val_str}</strong> ({card1_desvio_pct_str})</span>
          </div>
        </div>

        <!-- Card 2: Motores de Crescimento (Drivers & Ofensores) -->
        <div class="hero-card" id="cardMotores">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Motores de Venda</h3>
              <span class="hero-subtitle">Desempenho por Canal vs Meta</span>
            </div>
            <span class="hero-part-badge" style="background: #e0f2fe; color: #0284c7;">Canais</span>
          </div>

          <div class="driver-rows-list" id="driverRowsList">
            <!-- App -->
            <div class="driver-item" id="driverRowApp">
              <div class="driver-info-group">
                <span class="driver-name">📱 App</span>
                <span class="driver-share-tag" id="appShareTag">{app_share_str}</span>
              </div>
              <div class="driver-metrics-group">
                <span class="driver-sales-val" id="appSalesVal">{app_venda_str}</span>
                <span class="driver-badge-desv {app_badge_cls}" id="appBadgeDesv">{app_desv_str}</span>
              </div>
            </div>

            <!-- Marketplace -->
            <div class="driver-item" id="driverRowMkp">
              <div class="driver-info-group">
                <span class="driver-name">🛍️ MKP</span>
                <span class="driver-share-tag" id="mkpShareTag">{mkp_share_str}</span>
              </div>
              <div class="driver-metrics-group">
                <span class="driver-sales-val" id="mkpSalesVal">{mkp_venda_str}</span>
                <span class="driver-badge-desv {mkp_badge_cls}" id="mkpBadgeDesv">{mkp_desv_str}</span>
              </div>
            </div>

            <!-- Site -->
            <div class="driver-item" id="driverRowSite">
              <div class="driver-info-group">
                <span class="driver-name">💻 Site</span>
                <span class="driver-share-tag" id="siteShareTag">{site_share_str}</span>
              </div>
              <div class="driver-metrics-group">
                <span class="driver-sales-val" id="siteSalesVal">{site_venda_str}</span>
                <span class="driver-badge-desv {site_badge_cls}" id="siteBadgeDesv">{site_desv_str}</span>
              </div>
            </div>

            <!-- Figital (exibido dinamicamente) -->
            <div class="driver-item" id="driverRowFigital" style="display: none;">
              <div class="driver-info-group">
                <span class="driver-name">🏬 Figital</span>
                <span class="driver-share-tag" id="figShareTag">{fig_share_str}</span>
              </div>
              <div class="driver-metrics-group">
                <span class="driver-sales-val" id="figSalesVal">{fig_venda_str}</span>
                <span class="driver-badge-desv {fig_badge_cls}" id="figBadgeDesv">{fig_desv_str}</span>
              </div>
            </div>
          </div>

          <div class="card-insight-footer">
            <span>🚀</span> <span id="driverInsightTxt">App e MKP impulsionam <strong>+R$ 4,16 Mi</strong> acima da meta</span>
          </div>
        </div>

        <!-- Card 3: Eficiência Comercial (Ticket Médio & Margem) -->
        <div class="hero-card" id="cardEficiencia">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Eficiência Comercial</h3>
              <span class="hero-subtitle">Ticket Médio, Rentabilidade & Volume</span>
            </div>
            <span class="hero-part-badge" style="background: rgba(0, 119, 255, 0.1); color: var(--fsj-blue);">Rent: <strong id="effRentHeader">{rent_op_str}</strong></span>
          </div>

          <div class="efficiency-grid">
            <div class="efficiency-box">
              <span class="eff-lbl">Ticket Médio</span>
              <span class="eff-val" id="effTkmVal">{tkm_real_str}</span>
              <span class="eff-sub {tkm_cls}" id="effTkmSub">GAP R$: {tkm_gap_str}</span>
            </div>

            <div class="efficiency-box">
              <span class="eff-lbl">Rent. Operacional</span>
              <span class="eff-val" id="effRentVal">{rent_op_str}</span>
              <span class="eff-sub {rent_cls}" id="effRentSub">Meta: {rent_meta_str}</span>
            </div>

            <div class="efficiency-box">
              <span class="eff-lbl">Volume Pedidos</span>
              <span class="eff-val" id="effCuponsVal">{cupons_str}</span>
              <span class="eff-sub {cupons_cls}" id="effCuponsSub">Desvio: {cupons_desv_str}</span>
            </div>

            <div class="efficiency-box">
              <span class="eff-lbl">Evolução YoY</span>
              <span class="eff-val val-positive" id="effYoYVal">{evo_yoy_str}</span>
              <span class="eff-sub" style="color: var(--text-secondary);">vs mesmo período/25</span>
            </div>
          </div>

          <div class="card-insight-footer">
            <span>📊</span> <span>Volume acelerado de cupons compensa ticket médio mais baixo</span>
          </div>
        </div>

        <!-- Card 4: Ritmo Diário & Meta de Fechamento -->
        <div class="hero-card" id="cardRitmo">
          <div class="hero-header">
            <div class="hero-title-group">
              <h3>Meta de Fechamento</h3>
              <span class="hero-subtitle">Run Rate nos {dias_restantes} dias restantes</span>
            </div>
            <span class="hero-part-badge" id="ritmoAtingBadge" style="background: var(--badge-green-bg); color: var(--badge-green-text);">{ating_proj_str} da Meta</span>
          </div>

          <div class="runrate-grid">
            <div class="runrate-subrow">
              <span>Meta Diária Necessária:</span>
              <strong style="color: var(--fsj-blue-light); font-size: 13.5px;" id="ritmoDiariaNec">{diaria_nec_str}</strong>
            </div>
            <div class="runrate-subrow">
              <span>Ritmo Atual Apurado:</span>
              <strong class="val-positive" id="ritmoAtual">{run_rate_str}</strong>
            </div>
            <div class="runrate-subrow">
              <span>Meta Restante p/ 100%:</span>
              <strong id="ritmoMetaRest">{meta_rest_str}</strong>
            </div>
            <div class="runrate-subrow">
              <span>Fechamento Projetado:</span>
              <strong class="{proj_pos_cls}" id="ritmoFechamento">{fechamento_str}</strong>
            </div>
          </div>

          <div class="card-insight-footer">
            <span>🎯</span> <span id="ritmoInsightTxt">🟢 No ritmo atual, fecha com superação de <strong>{gap_fech_str}</strong></span>
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
            <span>GAP R$: <strong id="site_app-gap">{fmt_gap(kpis['site_app']['gap_venda_val'])}</strong></span>
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
          <h3>Faturamento Diário & GAP R$ vs Meta</h3>
          <div class="chart-legend-custom">
            <span class="legend-item"><span class="legend-dot" style="background: #cbd5e1;"></span> Faturamento Diário</span>
            <span class="legend-item"><span class="legend-dot" style="background: #0077ff;"></span> GAP Faturamento R$</span>
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

      <!-- Tabela de Origens de Tráfego / Canais de Mídia com Comparativo MoM / YoY e Ticket Médio -->
      <div class="traffic-table-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <h3 style="margin: 0; font-size: 16px; font-family: 'Outfit';">Desempenho por Origem de Tráfego / Canal de Mídia (GA4 Oficial)</h3>
              <span style="font-size: 11.5px; font-weight: 700; color: #059669; background: rgba(16, 185, 129, 0.1); padding: 3px 10px; border-radius: 6px;">
                ✓ 100% Dados Reais GA4
              </span>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;" id="trafficPeriodSubtitle">
              Propriedade Google Analytics: <strong>340874176</strong> | MTD 01 a {max_dia:02d}/09/2026 vs Base Anterior Pró-rata <strong>Agosto/2026 (01 a {max_dia:02d}/08)</strong>
            </div>
          </div>
          
          <div style="display: flex; align-items: center; gap: 8px;">
            <div class="diag-toggle-group">
              <button class="diag-toggle-btn active" id="btnTrafficMoM" onclick="setTrafficComparisonMode('mom')">
                <span>📅 vs Mês Anterior (MoM • Ago/26)</span>
              </button>
              <button class="diag-toggle-btn" id="btnTrafficYoY" onclick="setTrafficComparisonMode('yoy')">
                <span>🗓️ vs Ano Anterior (YoY • Set/25)</span>
              </button>
            </div>
          </div>
        </div>

        <div style="overflow-x: auto; -webkit-overflow-scrolling: touch;">
          <table class="data-table" id="trafficTable">
            <thead>
              <tr>
                <th>Origem / Mídia</th>
                <th>Canal</th>
                <th style="text-align: right;">Sessões</th>
                <th style="text-align: right;">Pedidos</th>
                <th style="text-align: right;">Tx. Conversão</th>
                <th style="text-align: right;">Ticket Médio</th>
                <th style="text-align: right;">Receita GA4 (R$)</th>
                <th style="text-align: right;" id="thTrafficBaseHeader">Base Ago/26 ({max_dia}d)</th>
                <th style="text-align: right;" id="thTrafficVarHeader">Var. MoM %</th>
                <th style="text-align: right;">Share</th>
              </tr>
            </thead>
            <tbody id="tbodyTraffic">
              <!-- Renderizado dinamicamente via renderTrafficTable -->
            </tbody>
            <tfoot id="tfootTraffic">
              <!-- Renderizado dinamicamente via renderTrafficTable -->
            </tfoot>
          </table>
        </div>
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
        renderTrafficTable(currentTrafficMode);
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

    // Formatação de Valores — Modelo pt-BR / GEMINI.md
    function fmtCurrency(val) {{
      if (val === null || val === undefined) return 'R$ 0';
      const absVal = Math.abs(val);
      const sign = val < 0 ? '-R$ ' : 'R$ ';
      if (absVal >= 1e6) {{
        return sign + (absVal / 1e6).toFixed(3).replace('.', ',') + ' Mi';
      }}
      if (absVal >= 1e3) {{
        return sign + (absVal / 1e3).toFixed(1).replace('.', ',') + ' K';
      }}
      return sign + Math.round(absVal).toLocaleString('pt-BR');
    }}

    function fmtGapVal(val) {{
      if (val === null || val === undefined) return 'R$ 0';
      const sign = val >= 0 ? '+' : '-';
      const absVal = Math.abs(val);
      if (absVal >= 1e6) {{
        return sign + 'R$ ' + (absVal / 1e6).toFixed(3).replace('.', ',') + ' Mi';
      }}
      if (absVal >= 1e3) {{
        return sign + 'R$ ' + (absVal / 1e3).toFixed(1).replace('.', ',') + ' K';
      }}
      return sign + 'R$ ' + Math.round(absVal).toLocaleString('pt-BR');
    }}

    function fmtPctStr(val) {{
      if (val === null || val === undefined) return '0,00%';
      const sign = val >= 0 ? '+' : '';
      return sign + val.toFixed(2).replace('.', ',') + '%';
    }}

    function fmtGrowthStr(val) {{
      if (val === null || val === undefined) return '—';
      if (val >= 0) return '⇑ +' + val.toFixed(1).replace('.', ',') + '%';
      return '⇓ -' + Math.abs(val).toFixed(1).replace('.', ',') + '%';
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
        const rent_op_desvio = rent_op_meta > 0 ? Number((((rent_op / rent_op_meta) - 1) * 100).toFixed(2)) : 0;
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

      // 1. Atualiza Card 1: Faturamento Consolidado
      const targetCons = m.canais_digitais || m.ecommerce_total;
      if (targetCons) {{
        setTxt('consTitle', isFigitalOn ? 'Canais Digitais (+ Figital)' : 'Canais Digitais');
        const consFigBadge = document.getElementById('consFigitalBadge');
        if (consFigBadge) consFigBadge.style.display = isFigitalOn ? 'inline-flex' : 'none';
        setTxt('consSubtitle', isFigitalOn ? 'Venda Efetiva (+ Figital no Período)' : 'Venda Efetiva no Período');
        setTxt('consPartBadge', 'Part: ' + targetCons.share_empresa.toFixed(2).replace('.', ',') + '%');
        setTxt('consMainVal', fmtCurrency(targetCons.venda));
        setTxt('consMetaMTD', fmtCurrency(targetCons.meta_mtd));
        setTxt('consGapVal', fmtGapVal(targetCons.gap_venda_val));
        setTxt('consDesvioPct', fmtPctStr(targetCons.desvio_venda_pct));

        const gapBanner = document.getElementById('consGapBanner');
        if (gapBanner) {{
          if (targetCons.gap_venda_val >= 0) {{
            gapBanner.className = 'hero-gap-banner';
          }} else {{
            gapBanner.className = 'hero-gap-banner negative';
          }}
        }}

        const atingMesPct = targetCons.meta_mes > 0 ? (targetCons.venda / targetCons.meta_mes * 100) : 0;
        setTxt('consProgPct', atingMesPct.toFixed(1).replace('.', ',') + '%');
        setTxt('consMetaMes', 'Meta: ' + fmtCurrency(targetCons.meta_mes));
        const progFill = document.getElementById('consProgFill');
        if (progFill) {{
          progFill.style.width = Math.min(100, atingMesPct).toFixed(1) + '%';
          const expectedMonthPct = (selectedDiaEnd / 30) * 100;
          if (atingMesPct >= expectedMonthPct) {{
            progFill.className = 'mini-progress-fill over-target';
          }} else {{
            progFill.className = 'mini-progress-fill';
          }}
        }}

        const consInsightTxt = document.getElementById('consInsightTxt');
        if (consInsightTxt) {{
          if (targetCons.gap_venda_val >= 0) {{
            consInsightTxt.innerHTML = `Superando a meta proporcional em <strong>${{fmtGapVal(targetCons.gap_venda_val)}}</strong> (${{fmtPctStr(targetCons.desvio_venda_pct)}})`;
          }} else {{
            consInsightTxt.innerHTML = `Abaixo da meta proporcional em <strong style="color: #dc2626;">${{fmtGapVal(targetCons.gap_venda_val)}}</strong> (${{fmtPctStr(targetCons.desvio_venda_pct)}})`;
          }}
        }}
      }}

      // 2. Atualiza Card 2: Motores de Venda
      const updateDriverRow = (prefix, data) => {{
        if (!data) return;
        setTxt(prefix + 'SalesVal', fmtCurrency(data.venda));
        setTxt(prefix + 'ShareTag', data.share_empresa.toFixed(2).replace('.', ',') + '%');
        setTxt(prefix + 'BadgeDesv', fmtPctStr(data.desvio_venda_pct));
        const badge = document.getElementById(prefix + 'BadgeDesv');
        if (badge) {{
          badge.className = 'driver-badge-desv ' + (data.gap_venda_val >= 0 ? 'badge-driver-pos' : 'badge-driver-neg');
        }}
      }};

      updateDriverRow('app', m.app);
      updateDriverRow('mkp', m.marketplace);
      updateDriverRow('site', m.site);

      const driverRowFig = document.getElementById('driverRowFigital');
      if (driverRowFig) {{
        if (isFigitalOn && m.figital) {{
          driverRowFig.style.display = 'flex';
          updateDriverRow('fig', m.figital);
        }} else {{
          driverRowFig.style.display = 'none';
        }}
      }}

      const driverInsightTxt = document.getElementById('driverInsightTxt');
      if (driverInsightTxt && m.app && m.marketplace) {{
        const supAppMkp = (m.app.gap_venda_val || 0) + (m.marketplace.gap_venda_val || 0);
        driverInsightTxt.innerHTML = `App e MKP impulsionam <strong>${{fmtGapVal(supAppMkp)}}</strong> acima da meta proporcional`;
      }}

      // 3. Atualiza Card 3: Eficiência Comercial
      if (targetCons) {{
        setTxt('effTkmVal', fmtCurrency(targetCons.tkm));
        const effTkmSub = document.getElementById('effTkmSub');
        if (effTkmSub) {{
          effTkmSub.textContent = `GAP R$: ${{fmtGapVal(targetCons.tkm_gap_val)}} (${{fmtPctStr(targetCons.tkm_desvio_pct)}})`;
          effTkmSub.className = 'eff-sub ' + (targetCons.tkm_gap_val >= 0 ? 'val-positive' : 'val-negative');
        }}

        setTxt('effRentVal', targetCons.rent_op.toFixed(2).replace('.', ',') + '%');
        setTxt('effRentHeader', targetCons.rent_op.toFixed(2).replace('.', ',') + '%');
        const effRentSub = document.getElementById('effRentSub');
        if (effRentSub) {{
          effRentSub.textContent = `Meta: ${{targetCons.rent_op_meta.toFixed(2).replace('.', ',')}}% • DRE: ${{targetCons.rent_dre.toFixed(2).replace('.', ',')}}%`;
          effRentSub.className = 'eff-sub ' + (targetCons.rent_op_desvio >= 0 ? 'val-positive' : 'val-negative');
        }}

        const cuponsStr = targetCons.cupons >= 1e3 ? (targetCons.cupons / 1e3).toFixed(2).replace('.', ',') + ' Mil' : targetCons.cupons.toLocaleString('pt-BR');
        setTxt('effCuponsVal', cuponsStr);
        const effCuponsSub = document.getElementById('effCuponsSub');
        if (effCuponsSub) {{
          effCuponsSub.textContent = `Desvio: ${{fmtPctStr(targetCons.cupons_desvio_pct)}} vs meta`;
          effCuponsSub.className = 'eff-sub ' + (targetCons.cupons_desvio_pct >= 0 ? 'val-positive' : 'val-negative');
        }}

        setTxt('effYoYVal', fmtGrowthStr(targetCons.evo_yoy));
      }}

      // 4. Atualiza Card 4: Ritmo Diário & Meta de Fechamento
      if (targetCons) {{
        const diasRest = Math.max(1, 30 - selectedDiaEnd);
        const metaRest = Math.max(0, targetCons.meta_mes - targetCons.venda);
        const diariaNec = metaRest / diasRest;
        const diasDecorridos = Math.max(1, selectedDiaEnd);
        const runRateAtual = targetCons.venda / diasDecorridos;
        const fechamentoProj = targetCons.venda + (runRateAtual * diasRest);
        const atingProj = targetCons.meta_mes > 0 ? (fechamentoProj / targetCons.meta_mes * 100) : 100;
        const gapFech = fechamentoProj - targetCons.meta_mes;

        setTxt('ritmoDiariaNec', fmtCurrency(diariaNec) + '/dia');
        setTxt('ritmoAtual', fmtCurrency(runRateAtual) + '/dia');
        setTxt('ritmoMetaRest', fmtCurrency(metaRest));
        setTxt('ritmoFechamento', fmtCurrency(fechamentoProj));
        setTxt('ritmoAtingBadge', atingProj.toFixed(1).replace('.', ',') + '% da Meta');

        const ritmoFechEl = document.getElementById('ritmoFechamento');
        if (ritmoFechEl) {{
          ritmoFechEl.className = gapFech >= 0 ? 'val-positive' : 'val-negative';
        }}

        const ritmoAtingBadge = document.getElementById('ritmoAtingBadge');
        if (ritmoAtingBadge) {{
          if (gapFech >= 0) {{
            ritmoAtingBadge.style.background = 'var(--badge-green-bg)';
            ritmoAtingBadge.style.color = 'var(--badge-green-text)';
          }} else {{
            ritmoAtingBadge.style.background = 'var(--badge-red-bg)';
            ritmoAtingBadge.style.color = 'var(--badge-red-text)';
          }}
        }}

        const ritmoInsightTxt = document.getElementById('ritmoInsightTxt');
        if (ritmoInsightTxt) {{
          if (gapFech >= 0) {{
            ritmoInsightTxt.innerHTML = `🟢 No ritmo atual, fecha com superação de <strong>${{fmtGapVal(gapFech)}}</strong>`;
          }} else {{
            ritmoInsightTxt.innerHTML = `⚠️ Necessário acelerar para <strong>${{fmtCurrency(diariaNec)}}/dia</strong> para atingir 100%`;
          }}
        }}
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

      // Determina atingimento e cores das barras (Vermelho = Abaixo da Meta, Azul = Meta Superada)
      const atingimentos = meses.map(m => isFigitalOn ? m.atingimento_total_com_figital_pct : m.atingimento_digitais_pct);
      const bgColors = atingimentos.map(ating => ating >= 100 
        ? (currentTheme === 'dark' ? '#38bdf8' : '#0077ff') 
        : (currentTheme === 'dark' ? '#f87171' : '#ef4444')
      );

      const realData = meses.map(m => isFigitalOn 
        ? Number(((m.real_digitais + (m.real_figital || 0)) / 1e6).toFixed(3))
        : Number((m.real_digitais / 1e6).toFixed(3))
      );

      const metaData = meses.map(m => isFigitalOn 
        ? Number(((m.meta_total_com_figital || m.meta_digitais) / 1e6).toFixed(3))
        : Number((m.meta_digitais / 1e6).toFixed(3))
      );

      // Atualiza textos da legenda no topo do card
      const legendTextReal = document.getElementById('legendTextReal');
      const legendTextMeta = document.getElementById('legendTextMeta');
      if (legendTextReal) legendTextReal.textContent = isFigitalOn ? 'Realizado (+ Figital)' : 'Realizado Canais Digitais';
      if (legendTextMeta) legendTextMeta.textContent = isFigitalOn ? 'Meta Oficial (+ Figital)' : 'Meta Oficial Digitais';

      const datasets = [
        {{
          type: 'bar',
          label: isFigitalOn ? 'Realizado (+ Figital)' : 'Realizado Canais Digitais',
          data: realData,
          backgroundColor: bgColors,
          borderRadius: 6,
          order: 2,
          datalabels: {{
            display: true,
            anchor: 'end',
            align: 'bottom',
            offset: 8,
            font: {{ size: 10.5, weight: '800' }},
            color: '#ffffff',
            formatter: val => 'R$ ' + val.toFixed(1).replace('.', ',') + 'M'
          }}
        }},
        {{
          type: 'line',
          label: isFigitalOn ? 'Meta Oficial (+ Figital)' : 'Meta Oficial Digitais',
          data: metaData,
          borderColor: currentTheme === 'dark' ? '#fbbf24' : '#003875',
          backgroundColor: 'transparent',
          borderWidth: 2.2,
          borderDash: [6, 4],
          pointRadius: 0,
          pointHoverRadius: 6,
          pointBackgroundColor: currentTheme === 'dark' ? '#fbbf24' : '#003875',
          tension: 0.15,
          order: 1,
          datalabels: {{ display: false }}
        }}
      ];

      chartAnualInstance = new Chart(ctx.getContext('2d'), {{
        data: {{
          labels: labels,
          datasets: datasets
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          layout: {{ padding: {{ top: 20, bottom: 8, left: 16, right: 16 }} }},
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
                  const lines = ['--------------------------'];
                  if (isFigitalOn && m.real_figital) {{
                    lines.push(`Digital Puro: R$ ${{(m.real_digitais/1e6).toFixed(2).replace('.', ',')}} Mi`);
                    lines.push(`Figital Lojas: R$ ${{(m.real_figital/1e6).toFixed(2).replace('.', ',')}} Mi`);
                    lines.push('--------------------------');
                  }}
                  const desvPct = ating - 100;
                  const desvPctStr = (desvPct >= 0 ? '+' : '') + desvPct.toFixed(1).replace('.', ',') + '%';
                  lines.push(`Desvio vs Meta: ${{desvPctStr}} (${{gapStr}})`);
                  lines.push(`Atingimento: ${{ating.toFixed(1).replace('.', ',')}}%`);
                  lines.push(ating >= 100 ? '🟢 Meta Superada' : '🔴 Abaixo da Meta');
                  lines.push('👉 Clique para abrir diagnóstico');
                  return lines;
                }}
              }}
            }}
          }},
          scales: {{
            y: {{
              grid: {{ color: getGridColor() }},
              suggestedMax: 66,
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
        const yoyPct = (diagData && diagData.yoy_cresc_pct != null) ? diagData.yoy_cresc_pct : 0;
        const yoySign = yoyPct >= 0 ? '+' : '';
        const yoyMesLbl = (diagData && diagData.yoy_mes_label) ? diagData.yoy_mes_label : '2025';
        const yoyBaseVal = (diagData && diagData.venda_yoy_base) ? diagData.venda_yoy_base : 0;

        if (subTitle) subTitle.textContent = `Comparativo estrutural de evolução anual (YoY) em relação a ${{yoyMesLbl}}.`;
        if (noticeBox) noticeBox.style.display = 'flex';
        if (noticeText) noticeText.innerHTML = `<strong>Evolução Anual (YoY):</strong> Comparação direta com ${{yoyMesLbl}} (${{yoySign}}${{yoyPct.toFixed(1).replace('.', ',')}}% de expansão digital) para mensurar ganho de escala e tração por categoria e linha.`;
        if (metric4Lbl) metric4Lbl.textContent = 'Evolução YoY';
        setEl('diagMoM', `${{yoySign}}${{yoyPct.toFixed(1).replace('.', ',')}}% vs ${{yoyMesLbl}}`, yoyPct >= 0 ? 'val-positive' : 'val-negative');
        setEl('diagYoY', `Base ${{yoyMesLbl}}: ${{fmtCurrency(yoyBaseVal)}}`, '');

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
                <span class="pct ${{cls}}">${{arrow}} ${{isDrop ? '-' : '+'}}${{Math.abs(l.delta_pct).toFixed(1).replace('.', ',')}}%</span>
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
                <span class="pct ${{cls}}">${{arrow}} ${{isDrop ? '-' : '+'}}${{Math.abs(l.delta_pct).toFixed(1).replace('.', ',')}}%</span>
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
      const legendFig = document.getElementById('annualLegendFigital');
      if (digFig) digFig.style.display = included ? 'inline-flex' : 'none';
      if (legendFig) legendFig.style.display = included ? 'inline-flex' : 'none';

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

        const bannerEl = document.getElementById('ytdDigGapBanner');
        if (bannerEl) {{
          bannerEl.className = digDesvVal >= 0 ? 'hero-gap-banner' : 'hero-gap-banner negative';
        }}
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
              suggestedMin: -25,
              suggestedMax: 25,
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
              label: 'GAP Faturamento R$',
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

    // =========================================================================
    // TABELA COMPARATIVA DE TRÁFEGO & CANAIS DE MÍDIA (GA4 OFICIAL)
    // =========================================================================
    let currentTrafficMode = 'mom';

    function setTrafficComparisonMode(mode) {{
      currentTrafficMode = mode;
      const btnMoM = document.getElementById('btnTrafficMoM');
      const btnYoY = document.getElementById('btnTrafficYoY');
      if (btnMoM && btnYoY) {{
        if (mode === 'mom') {{
          btnMoM.classList.add('active');
          btnYoY.classList.remove('active');
        }} else {{
          btnYoY.classList.add('active');
          btnMoM.classList.remove('active');
        }}
      }}
      renderTrafficTable(mode);
    }}

    function renderTrafficTable(mode) {{
      const origens = dashData.origens_trafego || [];
      const totais = dashData.trafego_totais || {{}};
      const maxD = dashData.max_dia || 17;
      const padD = String(maxD).padStart(2, '0');

      // Atualiza Headers e Subtítulo
      const subTitle = document.getElementById('trafficPeriodSubtitle');
      const thBase = document.getElementById('thTrafficBaseHeader');
      const thVar = document.getElementById('thTrafficVarHeader');

      if (mode === 'mom') {{
        if (subTitle) subTitle.innerHTML = `Propriedade Google Analytics: <strong>340874176</strong> | MTD 01 a ${{padD}}/09/2026 vs Base Anterior Pró-rata <strong>Agosto/2026 (01 a ${{padD}}/08)</strong>`;
        if (thBase) thBase.textContent = `Base Ago/26 (${{maxD}}d)`;
        if (thVar) thVar.textContent = 'Var. MoM %';
      }} else {{
        if (subTitle) subTitle.innerHTML = `Propriedade Google Analytics: <strong>340874176</strong> | MTD 01 a ${{padD}}/09/2026 vs Base Histórica <strong>Setembro/2025 (01 a ${{padD}}/09)</strong>`;
        if (thBase) thBase.textContent = `Base Set/25 (${{maxD}}d)`;
        if (thVar) thVar.textContent = 'Var. YoY %';
      }}

      // Renderiza Linhas do Corpo
      const tbody = document.getElementById('tbodyTraffic');
      if (tbody) {{
        tbody.innerHTML = origens.map(o => {{
          const cmp = (mode === 'mom' ? o.mom : o.yoy) || {{}};
          const tkmReal = o.ticket_medio || (o.pedidos > 0 ? o.receita / o.pedidos : 0);
          const tkmAnt = cmp.ticket_medio_ant || 0;
          const varRecPct = cmp.var_receita_pct || 0;
          const varSessPct = cmp.var_sessoes_pct || 0;
          const varTxConvPP = cmp.var_tx_conv_pp || 0;

          const recAnt = cmp.receita_ant || 0;
          const isRecPos = varRecPct >= 0;
          const isSessPos = varSessPct >= 0;
          const isTxPos = varTxConvPP >= 0;

          const txConvColor = o.tx_conv >= 0.05 ? '#16a34a' : '#2563eb';

          return `<tr>
            <td style="font-weight: 700; color: var(--text-primary); white-space: nowrap;">${{o.origem}}</td>
            <td><span style="display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; background: var(--bg-card-subtle); color: var(--text-secondary); white-space: nowrap;">${{o.canal}}</span></td>
            <td style="text-align: right;">
              <div style="font-weight: 700;">${{o.sessoes.toLocaleString('pt-BR')}}</div>
              <div style="font-size: 10.5px; font-weight: 600; color: ${{isSessPos ? '#16a34a' : '#dc2626'}};">
                ${{isSessPos ? '▲ +' : '▼ '}}${{varSessPct.toFixed(1).replace('.', ',')}}%
              </div>
            </td>
            <td style="text-align: right;">
              <div style="font-weight: 600;">${{o.pedidos.toLocaleString('pt-BR')}}</div>
              <div style="font-size: 10.5px; color: var(--text-secondary);">
                ${{cmp.pedidos_ant ? cmp.pedidos_ant.toLocaleString('pt-BR') + ' ant' : '-'}}
              </div>
            </td>
            <td style="text-align: right;">
              <div style="font-weight: 700; color: ${{txConvColor}};">${{(o.tx_conv * 100).toFixed(2).replace('.', ',')}}%</div>
              <div style="font-size: 10.5px; font-weight: 600; color: ${{isTxPos ? '#16a34a' : '#dc2626'}};">
                ${{isTxPos ? '▲ +' : '▼ '}}${{Math.abs(varTxConvPP).toFixed(2).replace('.', ',')}} p.p.
              </div>
            </td>
            <td style="text-align: right;">
              <div style="font-weight: 700;">R$ ${{Math.round(tkmReal).toLocaleString('pt-BR')}}</div>
              <div style="font-size: 10.5px; color: var(--text-secondary);">
                ${{tkmAnt > 0 ? 'Base: R$ ' + Math.round(tkmAnt).toLocaleString('pt-BR') : '-'}}
              </div>
            </td>
            <td style="text-align: right; font-weight: 800; color: var(--text-primary); white-space: nowrap;">
              R$ ${{Math.round(o.receita).toLocaleString('pt-BR')}}
            </td>
            <td style="text-align: right; font-weight: 600; color: var(--text-secondary); white-space: nowrap;">
              R$ ${{Math.round(recAnt).toLocaleString('pt-BR')}}
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <span style="display: inline-flex; align-items: center; gap: 3px; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: var(--radius-pill); background: ${{isRecPos ? 'var(--badge-green-bg)' : 'var(--badge-red-bg)'}}; color: ${{isRecPos ? 'var(--badge-green-text)' : 'var(--badge-red-text)'}};">
                ${{isRecPos ? '▲ +' : '▼ '}}${{Math.abs(varRecPct).toFixed(1).replace('.', ',')}}%
              </span>
            </td>
            <td style="text-align: right; font-weight: 600; color: var(--text-secondary);">
              ${{(o.share * 100).toFixed(1).replace('.', ',')}}%
            </td>
          </tr>`;
        }}).join('');
      }}

      // Renderiza Rodapé Consolidado
      const tfoot = document.getElementById('tfootTraffic');
      if (tfoot) {{
        const totCmp = (mode === 'mom' ? totais.mom : totais.yoy) || {{}};
        const totSess = totais.sessoes || 0;
        const totPed = totais.pedidos || 0;
        const totTx = totais.tx_conv || 0;
        const totTkm = totais.ticket_medio || (totPed > 0 ? totais.receita / totPed : 0);
        const totRec = totais.receita || 0;
        const totRecAnt = totCmp.receita_ant || 0;
        const totVarRecPct = totCmp.var_receita_pct || 0;
        const totVarSessPct = totCmp.var_sessoes_pct || 0;
        const totVarTxPP = totCmp.var_tx_conv_pp || 0;
        const totTkmAnt = totCmp.ticket_medio_ant || 0;

        const isTotRecPos = totVarRecPct >= 0;
        const isTotSessPos = totVarSessPct >= 0;
        const isTotTxPos = totVarTxPP >= 0;

        tfoot.innerHTML = `
          <tr style="font-weight: 800; background: var(--bg-card-subtle); border-top: 2px solid var(--border-card);">
            <td style="font-weight: 800; color: var(--text-primary); white-space: nowrap;">TOTAL CONSOLIDADO GA4</td>
            <td><span style="display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; background: rgba(0, 86, 179, 0.1); color: var(--fsj-blue); white-space: nowrap;">Site + App</span></td>
            <td style="text-align: right;">
              <div style="font-weight: 800;">${{totSess.toLocaleString('pt-BR')}}</div>
              <div style="font-size: 11px; font-weight: 700; color: ${{isTotSessPos ? '#16a34a' : '#dc2626'}};">
                ${{isTotSessPos ? '▲ +' : '▼ '}}${{totVarSessPct.toFixed(1).replace('.', ',')}}%
              </div>
            </td>
            <td style="text-align: right;">
              <div style="font-weight: 800;">${{totPed.toLocaleString('pt-BR')}}</div>
              <div style="font-size: 11px; color: var(--text-secondary);">
                ${{totCmp.pedidos_ant ? totCmp.pedidos_ant.toLocaleString('pt-BR') + ' ant' : '-'}}
              </div>
            </td>
            <td style="text-align: right;">
              <div style="font-weight: 800; color: #16a34a;">${{totTx.toFixed(2).replace('.', ',')}}%</div>
              <div style="font-size: 11px; font-weight: 700; color: ${{isTotTxPos ? '#16a34a' : '#dc2626'}};">
                ${{isTotTxPos ? '▲ +' : '▼ '}}${{Math.abs(totVarTxPP).toFixed(2).replace('.', ',')}} p.p.
              </div>
            </td>
            <td style="text-align: right;">
              <div style="font-weight: 800;">R$ ${{Math.round(totTkm).toLocaleString('pt-BR')}}</div>
              <div style="font-size: 11px; color: var(--text-secondary);">
                ${{totTkmAnt > 0 ? 'Base: R$ ' + Math.round(totTkmAnt).toLocaleString('pt-BR') : '-'}}
              </div>
            </td>
            <td style="text-align: right; font-weight: 800; color: var(--fsj-blue); white-space: nowrap;">
              R$ ${{Math.round(totRec).toLocaleString('pt-BR')}}
            </td>
            <td style="text-align: right; font-weight: 700; color: var(--text-secondary); white-space: nowrap;">
              R$ ${{Math.round(totRecAnt).toLocaleString('pt-BR')}}
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <span style="display: inline-flex; align-items: center; gap: 3px; font-weight: 800; font-size: 11.5px; padding: 3px 10px; border-radius: var(--radius-pill); background: ${{isTotRecPos ? 'var(--badge-green-bg)' : 'var(--badge-red-bg)'}}; color: ${{isTotRecPos ? 'var(--badge-green-text)' : 'var(--badge-red-text)'}};">
                ${{isTotRecPos ? '▲ +' : '▼ '}}${{Math.abs(totVarRecPct).toFixed(1).replace('.', ',')}}%
              </span>
            </td>
            <td style="text-align: right; font-weight: 800; color: var(--text-primary);">100,0%</td>
          </tr>
        `;
      }}
    }}

    // Inicialização da UI com preferências salvas
    applyFigitalToggle(isFigitalOn);
    initAnnualView();
    renderTrafficTable(currentTrafficMode);
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
