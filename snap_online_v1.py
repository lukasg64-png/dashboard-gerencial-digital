import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        url = f"https://lukasg64-png.github.io/dashboard-gerencial-digital/?_t={int(time.time())}"
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_timeout(1000)
        await page.click('button[data-view="view-geral"]')
        await page.wait_for_timeout(1000)
        
        art_dir = r"C:\Users\lucas.alves6\.gemini\antigravity-ide\brain\594c4f25-5ab9-41a5-a963-ee3589f2467e"
        target = os.path.join(art_dir, "audit_online_visao1.png")
        await page.screenshot(path=target)
        print("Salvo em:", target)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
