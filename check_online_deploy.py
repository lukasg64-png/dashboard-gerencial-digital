import asyncio
import time
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={'width': 1920, 'height': 1080})
        cache_buster = str(int(time.time()))
        url = f'https://lukasg64-png.github.io/dashboard-gerencial-digital/?t={cache_buster}'
        print(f"Acessando: {url}")
        res = await page.goto(url)
        print("HTTP Status:", res.status)
        await page.wait_for_timeout(2000)
        exists = await page.locator('#btnTrafficMoM').count()
        print('Online btnTrafficMoM exists:', exists > 0)
        if exists > 0:
            traffic_tab = page.locator('.nav-btn[data-view="view-trafego"]')
            await traffic_tab.click()
            await page.wait_for_timeout(500)
            table_card = page.locator('.traffic-table-card')
            await table_card.scroll_into_view_if_needed()
            path = r"C:\Users\lucas.alves6\.gemini\antigravity-ide\brain\8b979918-3271-4a70-99ee-133956b05a83\online_traffic_mom.png"
            await table_card.screenshot(path=path)
            print(f"Screenshot salvo em {path}")
        await b.close()

if __name__ == '__main__':
    asyncio.run(check())
