import asyncio
import os
import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def audit():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'index.html').replace('\\', '/')
    file_url = f"file:///{html_path}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Janela de 1920x2200 para capturar todos os gráficos sem rolagem
        page = await browser.new_page(viewport={'width': 1920, 'height': 2200})
        await page.goto(file_url, wait_until='networkidle')
        await page.wait_for_timeout(800)

        # 1. Visão 2: Tendências e Desvios
        await page.click('button[data-view="view-desvios"]')
        await page.wait_for_timeout(800)
        shot_v2 = os.path.join(base_dir, 'audit_visao_2_completa.png')
        await page.screenshot(path=shot_v2)
        print("✅ Visão 2 completa salva:", shot_v2)

        # 2. Visão 3: Tráfego e Conversão (App)
        await page.click('button[data-view="view-trafego"]')
        await page.wait_for_timeout(800)
        shot_v3 = os.path.join(base_dir, 'audit_visao_3_completa.png')
        await page.screenshot(path=shot_v3)
        print("✅ Visão 3 completa (App) salva:", shot_v3)

        # 3. Visão 3: Tráfego e Conversão (Site)
        await page.click('button[data-traffic-ch="site"]')
        await page.wait_for_timeout(800)
        shot_v3_site = os.path.join(base_dir, 'audit_visao_3_site.png')
        await page.screenshot(path=shot_v3_site)
        print("✅ Visão 3 completa (Site) salva:", shot_v3_site)

        await browser.close()
        print("Auditoria visual concluída!")

if __name__ == '__main__':
    asyncio.run(audit())
