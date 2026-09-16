import asyncio
import os
import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def verify():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'index.html').replace('\\', '/')
    file_url = f"file:///{html_path}"
    print("Testing URL:", file_url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})

        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.on('console', lambda msg: print(f"[Console {msg.type}]:", msg.text) if msg.type in ['error', 'warn'] else None)

        await page.goto(file_url, wait_until='networkidle')
        await page.wait_for_timeout(1000)

        # Screenshot Visão 1
        shot1 = os.path.join(base_dir, 'preview_visao_1_geral.png')
        await page.screenshot(path=shot1, full_page=False)
        print("✅ Visão 1 screenshot salvo:", shot1)

        # Clica na Visão 2 (Tendências & Desvios)
        await page.click('button[data-view="view-desvios"]')
        await page.wait_for_timeout(1000)
        shot2 = os.path.join(base_dir, 'preview_visao_2_desvios.png')
        await page.screenshot(path=shot2, full_page=False)
        print("✅ Visão 2 screenshot salvo:", shot2)

        # Clica na Visão 3 (Tráfego & Conversão)
        await page.click('button[data-view="view-trafego"]')
        await page.wait_for_timeout(1000)
        shot3 = os.path.join(base_dir, 'preview_visao_3_trafego.png')
        await page.screenshot(path=shot3, full_page=False)
        print("✅ Visão 3 screenshot salvo:", shot3)

        # Clica na Visão 4 (Projeções & Fechamento)
        await page.click('button[data-view="view-projecoes"]')
        await page.wait_for_timeout(1000)
        shot4 = os.path.join(base_dir, 'preview_visao_4_projecoes.png')
        await page.screenshot(path=shot4, full_page=False)
        print("✅ Visão 4 screenshot salvo:", shot4)

        await browser.close()

        if errors:
            print("❌ Erros JS encontrados:", errors)
        else:
            print("🎉 Zero erros de página detectados!")

if __name__ == '__main__':
    asyncio.run(verify())
