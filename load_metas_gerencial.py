"""
load_metas_gerencial.py — Carrega e Estrutura as Metas Diárias Oficiais do Varejo Digital.
Fonte: base Gerencial.xlsx (Abas: METAS e Metas Sessoes e TX conversao).
Gera:
- data/metas_gerencial_diaria.json: Série temporal diária completa com metas de vendas, cupons, TKM, margem, sessões e tx conversão.
- data/metas_gerencial_resumo.json: Metas mensais consolidadas por canal para 2026.
"""
import os
import sys
import json
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

EXCEL_PATH = os.path.join(BASE_DIR, 'base Gerencial.xlsx')

def load_and_process_metas():
    print("=" * 70)
    print("  CARREGANDO METAS GERENCIAIS DE 2026 (base Gerencial.xlsx)")
    print("=" * 70)

    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Arquivo de metas não encontrado: {EXCEL_PATH}")

    # 1. Carregar aba METAS
    print("1. Lendo aba METAS...", flush=True)
    df_metas = pd.read_excel(EXCEL_PATH, sheet_name='METAS')
    df_metas['DATA'] = pd.to_datetime(df_metas['DATA'])
    df_metas = df_metas.dropna(subset=['DATA']).sort_values('DATA').reset_index(drop=True)

    # 2. Carregar aba Metas Sessoes e TX conversao
    print("2. Lendo aba Metas Sessoes e TX conversao...", flush=True)
    df_sessoes = pd.read_excel(EXCEL_PATH, sheet_name='Metas Sessoes e TX conversao')
    df_sessoes['DATA'] = pd.to_datetime(df_sessoes['DATA'])
    df_sessoes = df_sessoes.dropna(subset=['DATA']).sort_values('DATA').reset_index(drop=True)

    # Renomeia colunas para padrão limpo
    cols_sessoes = df_sessoes.columns.tolist()
    rename_sessoes = {
        'Meta Sessoes APP': 'meta_sessoes_app',
        'Meta Taxa Conv. APP': 'meta_tx_conv_app',
        'Meta Sessoes Site': 'meta_sessoes_site',
    }
    if len(cols_sessoes) >= 5:
        rename_sessoes[cols_sessoes[4]] = 'meta_tx_conv_site'
    if len(cols_sessoes) >= 6:
        rename_sessoes[cols_sessoes[5]] = 'meta_sessoes_site_app'
    
    df_sessoes = df_sessoes.rename(columns=rename_sessoes)

    # Merge das duas abas por DATA
    df_merged = pd.merge(df_metas, df_sessoes, on='DATA', how='left')

    def safe_float(val, default=0.0):
        if val is None or pd.isna(val):
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    daily_dict = {}
    monthly_summary = {}

    for idx, row in df_merged.iterrows():
        dt = row['DATA']
        if pd.isna(dt) or not hasattr(dt, 'strftime'):
            continue
        date_str = dt.strftime('%Y-%m-%d')
        ano_mes = dt.strftime('%Y-%m')
        dia = dt.day

        # APP
        v_app = safe_float(row.get('Meta APP Venda'))
        c_app = safe_float(row.get('Meta APP Cupons'))
        tkm_app = safe_float(row.get('Meta APP TKM'), (v_app / c_app if c_app > 0 else 0.0))
        mg_pct_app = safe_float(row.get('Meta Margem %'), 0.215)
        mg_val_app = safe_float(row.get('Meta APP Margem $'), (v_app * mg_pct_app))
        sess_app = safe_float(row.get('meta_sessoes_app'))
        tx_app = safe_float(row.get('meta_tx_conv_app'), 0.0831)

        # SITE
        v_site = safe_float(row.get('Meta SITE Venda'))
        c_site = safe_float(row.get('Meta Site Cupons'))
        tkm_site = safe_float(row.get('Meta Site TKM'), (v_site / c_site if c_site > 0 else 0.0))
        mg_pct_site = safe_float(row.get('Meta SITE Margem %'), 0.215)
        mg_val_site = safe_float(row.get('Meta SITE Margem $'), (v_site * mg_pct_site))
        sess_site = safe_float(row.get('meta_sessoes_site'))
        tx_site = safe_float(row.get('meta_tx_conv_site'), 0.0266)

        # MARKETPLACE
        v_mkp = safe_float(row.get('Meta MKP Venda'))
        c_mkp = safe_float(row.get('Meta MKP Cupons'))
        tkm_mkp = safe_float(row.get('Meta MKP TKM'), (v_mkp / c_mkp if c_mkp > 0 else 0.0))
        mg_pct_mkp = safe_float(row.get('Meta Ifood Margem %'), 0.315)
        mg_val_mkp = safe_float(row.get('Meta MKP Margem $'), (v_mkp * mg_pct_mkp))

        # TELEVENDAS
        v_tele = safe_float(row.get('Meta Televendas Venda'))
        c_tele = safe_float(row.get('Meta Televendas Cupons'))
        tkm_tele = safe_float(row.get('Meta Televendas TKM'), (v_tele / c_tele if c_tele > 0 else 0.0))
        mg_pct_tele = safe_float(row.get('Meta Televendas Margem %'), 0.22)
        mg_val_tele = safe_float(row.get('Meta Televendas Margem $'), (v_tele * mg_pct_tele))

        # CONSOLIDADOS
        # Site + App
        v_site_app = v_site + v_app
        c_site_app = c_site + c_app
        tkm_site_app = v_site_app / c_site_app if c_site_app > 0 else 0.0
        sess_site_app = safe_float(row.get('meta_sessoes_site_app'), (sess_app + sess_site))
        tx_site_app = (c_site_app / sess_site_app) if sess_site_app > 0 else ((tx_app * sess_app + tx_site * sess_site) / sess_site_app if sess_site_app > 0 else 0.0)

        # Canais Digitais (Site + App + Marketplace)
        v_digitais = v_site + v_app + v_mkp
        c_digitais = c_site + c_app + c_mkp
        tkm_digitais = v_digitais / c_digitais if c_digitais > 0 else 0.0
        mg_val_digitais = mg_val_app + mg_val_site + mg_val_mkp
        mg_pct_digitais = mg_val_digitais / v_digitais if v_digitais > 0 else 0.24

        # E-Commerce Total (Canais Digitais + Televendas)
        v_ecom = v_digitais + v_tele
        c_ecom = c_digitais + c_tele
        tkm_ecom = v_ecom / c_ecom if c_ecom > 0 else 0.0
        mg_val_ecom = mg_val_digitais + mg_val_tele
        mg_pct_ecom = mg_val_ecom / v_ecom if v_ecom > 0 else 0.24

        daily_dict[date_str] = {
            'data': date_str,
            'ano_mes': ano_mes,
            'dia': dia,
            'app': {
                'venda': v_app, 'cupons': c_app, 'tkm': tkm_app,
                'margem_pct': mg_pct_app, 'margem_val': mg_val_app,
                'sessoes': sess_app, 'tx_conv': tx_app
            },
            'site': {
                'venda': v_site, 'cupons': c_site, 'tkm': tkm_site,
                'margem_pct': mg_pct_site, 'margem_val': mg_val_site,
                'sessoes': sess_site, 'tx_conv': tx_site
            },
            'marketplace': {
                'venda': v_mkp, 'cupons': c_mkp, 'tkm': tkm_mkp,
                'margem_pct': mg_pct_mkp, 'margem_val': mg_val_mkp
            },
            'televendas': {
                'venda': v_tele, 'cupons': c_tele, 'tkm': tkm_tele,
                'margem_pct': mg_pct_tele, 'margem_val': mg_val_tele
            },
            'site_app': {
                'venda': v_site_app, 'cupons': c_site_app, 'tkm': tkm_site_app,
                'sessoes': sess_site_app, 'tx_conv': tx_site_app
            },
            'canais_digitais': {
                'venda': v_digitais, 'cupons': c_digitais, 'tkm': tkm_digitais,
                'margem_pct': mg_pct_digitais, 'margem_val': mg_val_digitais
            },
            'ecommerce_total': {
                'venda': v_ecom, 'cupons': c_ecom, 'tkm': tkm_ecom,
                'margem_pct': mg_pct_ecom, 'margem_val': mg_val_ecom
            }
        }

        # Agregacao mensal
        if ano_mes not in monthly_summary:
            monthly_summary[ano_mes] = {
                'app': {'venda': 0.0, 'cupons': 0.0, 'margem_val': 0.0, 'sessoes': 0.0},
                'site': {'venda': 0.0, 'cupons': 0.0, 'margem_val': 0.0, 'sessoes': 0.0},
                'marketplace': {'venda': 0.0, 'cupons': 0.0, 'margem_val': 0.0},
                'televendas': {'venda': 0.0, 'cupons': 0.0, 'margem_val': 0.0},
                'site_app': {'venda': 0.0, 'cupons': 0.0, 'sessoes': 0.0},
                'canais_digitais': {'venda': 0.0, 'cupons': 0.0, 'margem_val': 0.0},
                'ecommerce_total': {'venda': 0.0, 'cupons': 0.0, 'margem_val': 0.0}
            }
        
        m = monthly_summary[ano_mes]
        m['app']['venda'] += v_app
        m['app']['cupons'] += c_app
        m['app']['margem_val'] += mg_val_app
        m['app']['sessoes'] += sess_app

        m['site']['venda'] += v_site
        m['site']['cupons'] += c_site
        m['site']['margem_val'] += mg_val_site
        m['site']['sessoes'] += sess_site

        m['marketplace']['venda'] += v_mkp
        m['marketplace']['cupons'] += c_mkp
        m['marketplace']['margem_val'] += mg_val_mkp

        m['televendas']['venda'] += v_tele
        m['televendas']['cupons'] += c_tele
        m['televendas']['margem_val'] += mg_val_tele

        m['site_app']['venda'] += v_site_app
        m['site_app']['cupons'] += c_site_app
        m['site_app']['sessoes'] += sess_site_app

        m['canais_digitais']['venda'] += v_digitais
        m['canais_digitais']['cupons'] += c_digitais
        m['canais_digitais']['margem_val'] += mg_val_digitais

        m['ecommerce_total']['venda'] += v_ecom
        m['ecommerce_total']['cupons'] += c_ecom
        m['ecommerce_total']['margem_val'] += mg_val_ecom

    # Calcula médias e taxas mensais
    for ano_mes, m in monthly_summary.items():
        for k in ['app', 'site', 'marketplace', 'televendas', 'site_app', 'canais_digitais', 'ecommerce_total']:
            v = m[k]['venda']
            c = m[k]['cupons']
            m[k]['tkm'] = v / c if c > 0 else 0.0
            if 'margem_val' in m[k]:
                m[k]['margem_pct'] = m[k]['margem_val'] / v if v > 0 else 0.0
            if 'sessoes' in m[k]:
                s = m[k]['sessoes']
                m[k]['tx_conv'] = c / s if s > 0 else 0.0

    # Salva arquivos JSON
    out_diaria = os.path.join(DATA_DIR, 'metas_gerencial_diaria.json')
    with open(out_diaria, 'w', encoding='utf-8') as f:
        json.dump(daily_dict, f, ensure_ascii=False, indent=2)
    print(f"✅ Salvo: {out_diaria} ({len(daily_dict)} dias)", flush=True)

    out_resumo = os.path.join(DATA_DIR, 'metas_gerencial_resumo.json')
    with open(out_resumo, 'w', encoding='utf-8') as f:
        json.dump(monthly_summary, f, ensure_ascii=False, indent=2)
    print(f"✅ Salvo: {out_resumo} ({len(monthly_summary)} meses)", flush=True)

    # Validação rápida de Setembro/2026
    if '2026-09' in monthly_summary:
        set26 = monthly_summary['2026-09']
        print("\n--- Validação Setembro/2026 ---")
        print(f"Meta Mês Canais Digitais: R$ {set26['canais_digitais']['venda']:,.2f}")
        print(f"Meta Mês E-Commerce Total: R$ {set26['ecommerce_total']['venda']:,.2f}")
        print(f"Meta Mês App: R$ {set26['app']['venda']:,.2f}")
        print(f"Meta Mês Site: R$ {set26['site']['venda']:,.2f}")
        print(f"Meta Mês Marketplace: R$ {set26['marketplace']['venda']:,.2f}")
        print(f"Meta Mês Televendas: R$ {set26['televendas']['venda']:,.2f}")

    return daily_dict, monthly_summary

if __name__ == '__main__':
    load_and_process_metas()
