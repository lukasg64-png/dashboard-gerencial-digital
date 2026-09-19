import asyncio
import os
import sys
import json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

QLIK_CLOUD_HOST = "fsj.us.qlikcloud.com"
STORAGE_STATE = r"c:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\Acompanhamento Categorias Digital\data\qlik_cloud_storage_state.json"
APP_ID = "dcfc3ede-5eab-407c-a9ce-12b546eb5bdf" # Vendas Análise - Analítico

async def check_dates():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=STORAGE_STATE, ignore_https_errors=True)
        page = await context.new_page()
        
        print("Conectando ao Qlik Cloud...", flush=True)
        await page.goto(f"https://{QLIK_CLOUD_HOST}/analytics/home", timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("Consultando datas máximas e reloads no App Vendas Análise - Analítico...", flush=True)
        res = await page.evaluate(f'''async () => {{
            const appId = "{APP_ID}";
            const csrfRes = await fetch('/api/v1/csrf-token');
            const csrfToken = csrfRes.headers.get('qlik-csrf-token');
            const wsUrl = `wss://${{window.location.host}}/app/${{encodeURIComponent(appId)}}?qlik-csrf-token=${{csrfToken}}`;
            return new Promise((resolve, reject) => {{
                const ws = new WebSocket(wsUrl);
                let msgId = 1;
                const pending = {{}};
                function send(method, handle, params) {{
                    return new Promise((res, rej) => {{
                        const id = msgId++;
                        pending[id] = {{ res, rej }};
                        ws.send(JSON.stringify({{ "jsonrpc": "2.0", "id": id, "method": method, "handle": handle, "params": params }}));
                    }});
                }}
                ws.onmessage = evt => {{
                    const d = JSON.parse(evt.data);
                    if (d.id && pending[d.id]) {{
                        if (d.error) pending[d.id].rej(d.error);
                        else pending[d.id].res(d);
                    }}
                }};
                ws.onerror = err => reject(String(err));
                ws.onopen = async () => {{
                    try {{
                        const openRes = await send("OpenDoc", -1, [appId]);
                        const docHandle = openRes.result.qReturn.qHandle;
                        
                        // 1. Avalia expressões de data máxima
                        const exprs = [
                            "Max([Data])",
                            "Max([Data Venda])",
                            "Max([Data Movimento])",
                            "Date(Max([Data]), 'DD/MM/YYYY')",
                            "Max([Dia])",
                            "Max(num#(Dia))",
                            "Max({{1<[Ano-Mes]={{'2026-09'}}>}} [Dia])",
                            "Max({{1<[Ano-Mes]={{'2026-09'}}>}} num#(Dia))"
                        ];
                        
                        const evalResults = {{}};
                        for (const exp of exprs) {{
                            try {{
                                const r = await send("EvaluateEx", docHandle, [exp]);
                                evalResults[exp] = r.result.qValue;
                            }} catch(e) {{
                                evalResults[exp] = {{ error: String(e) }};
                            }}
                        }}
                        
                        // 2. Tabela com últimos 10 dias distintos com venda em Setembro/2026
                        let diasTable = [];
                        try {{
                            const cube = await send("CreateSessionObject", docHandle, [{{
                                "qInfo": {{ "qType": "q_dias" }},
                                "qHyperCubeDef": {{
                                    "qDimensions": [{{ "qDef": {{ "qFieldDefs": ["Dia"] }} }}],
                                    "qMeasures": [
                                        {{ "qDef": {{ "qDef": "Sum({{1<[Ano-Mes]={{'2026-09'}}>}} [Venda Líquida])" }} }}
                                    ],
                                    "qInitialDataFetch": [{{ "qTop": 0, "qLeft": 0, "qHeight": 35, "qWidth": 2 }}],
                                    "qSuppressZero": true
                                }}
                            }}]);
                            const cHandle = cube.result.qReturn.qHandle;
                            const layout = await send("GetLayout", cHandle, []);
                            const matrix = layout.result.qLayout.qHyperCube.qDataPages[0].qMatrix;
                            diasTable = matrix.map(row => ({{
                                dia: row[0].qText,
                                venda: row[1].qNum
                            }}));
                        }} catch(e) {{
                            diasTable = {{ error: String(e) }};
                        }}
                        
                        resolve({{ evalResults, diasTable }});
                    }} catch(e) {{
                        reject(String(e));
                    }}
                }};
            }});
        }}''')
        
        await browser.close()
        return res

if __name__ == '__main__':
    result = asyncio.run(check_dates())
    print("\n--- RESULTADOS DAS EXPRESSÕES NO QLIK CLOUD ---")
    for exp, val in result.get('evalResults', {}).items():
        print(f"  {exp:45s} -> {val}")
        
    print("\n--- DIAS COM VENDA EM SETEMBRO/2026 NO APP ---")
    dias = result.get('diasTable', [])
    if isinstance(dias, list):
        # ordena por dia numérico
        dias_sorted = sorted([d for d in dias if d.get('dia', '').isdigit()], key=lambda x: int(x['dia']))
        for d in dias_sorted:
            print(f"  Dia {int(d['dia']):02d}: R$ {d['venda']:,.2f}")
        if dias_sorted:
            print(f"\n=> MÁXIMO DIA COM VENDA NO QLIK CLOUD HOJE: DIA {int(dias_sorted[-1]['dia']):02d}")
    else:
        print("Tabela de dias:", dias)
