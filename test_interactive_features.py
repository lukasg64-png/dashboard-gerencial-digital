import asyncio
import os
from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = "file://" + os.path.join(BASE_DIR, "index.html").replace("\\", "/")

async def main():
    print("Iniciando auditoria dos recursos interativos no navegador...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})

        # Registra erros de console se houver
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto(HTML_PATH)
        await page.wait_for_timeout(1500)

        # 1. Validação MTD Inicial (01 a 17/09)
        ecom_val = await page.locator("#ecomMainVal").text_content()
        dig_val = await page.locator("#digMainVal").text_content()
        app_val = await page.locator("#app-header-venda").text_content()
        site_val = await page.locator("#site-header-venda").text_content()
        mkp_val = await page.locator("#mkp-header-venda").text_content()
        fig_val = await page.locator("#figitalMainVal").text_content()

        print(f"[MTD Inicial] E-Com: {ecom_val} | Digitais: {dig_val} | App: {app_val} | Site: {site_val} | MKP: {mkp_val} | Figital: {fig_val}")
        assert "33" in ecom_val, f"Ecom esperado ~33M, obtido: {ecom_val}"
        assert "17" in app_val, f"App esperado ~17M, obtido: {app_val}"
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_01_mtd.png"))

        # 2. Testar Filtro de Período: Ontem (D-1: 17/09)
        print("Testando filtro: Ontem D-1 (17/09)...")
        await page.select_option("#periodFilter", "d1")
        await page.wait_for_timeout(500)

        ecom_d1 = await page.locator("#ecomMainVal").text_content()
        app_d1 = await page.locator("#app-header-venda").text_content()
        print(f"[Ontem D-1] E-Com: {ecom_d1} | App: {app_d1}")
        assert ecom_d1 != ecom_val, "O valor de E-Com deveria mudar ao filtrar por D-1!"
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_02_d1.png"))

        # 3. Testar Histórico Diário (Selecionar Dia Específico)
        print("Testando seletor de dia individual (Histórico Diário)...")
        await page.select_option("#periodFilter", "day")
        await page.wait_for_timeout(500)

        is_day_box_visible = await page.locator("#daySelectBox").is_visible()
        print(f"Day select box visível: {is_day_box_visible}")
        assert is_day_box_visible, "O seletor de dia individual deve ficar visível ao escolher 'day'!"

        # Seleciona dia 09 (dia de forte promoção)
        await page.select_option("#dayHistorySelect", "9")
        await page.wait_for_timeout(500)
        app_d9 = await page.locator("#app-header-venda").text_content()
        print(f"[Histórico Dia 09/09] Venda App: {app_d9}")
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_03_dia09.png"))

        # 4. Voltar para MTD e Testar Toggle Figital (ON / OFF)
        print("Testando Toggle Figital...")
        await page.select_option("#periodFilter", "mtd")
        await page.wait_for_timeout(500)

        ecom_before_fig = await page.locator("#ecomMainVal").text_content()
        # Clica no switch do Figital
        await page.click("#figitalSwitchBar")
        await page.wait_for_timeout(500)

        ecom_after_fig = await page.locator("#ecomMainVal").text_content()
        badge_state = await page.locator("#figitalStateBadge").text_content()
        print(f"[Figital Toggle ON] E-Com antes: {ecom_before_fig} | E-Com depois: {ecom_after_fig} | Badge: {badge_state}")
        assert badge_state == "ON", "O badge do Figital deveria estar em ON!"
        assert ecom_after_fig != ecom_before_fig, "O valor com Figital deve somar o faturamento Figital!"
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_04_figital_on.png"))

        # 5. Navegação entre Visões (Visão 2: Tendências, Visão 3: Tráfego, Visão 4: Projeções)
        print("Testando navegação nas visões...")
        await page.click("button[data-view='view-desvios']")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_05_visao2.png"))

        await page.click("button[data-view='view-trafego']")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_06_visao3.png"))

        await page.click("button[data-view='view-projecoes']")
        await page.wait_for_timeout(600)
        proj_real_ecom = await page.locator("#proj-real-ecommerce_total").text_content()
        print(f"[Visão 4 Projeções] Realizado E-Com: {proj_real_ecom}")
        await page.screenshot(path=os.path.join(BASE_DIR, "audit_07_visao4.png"))

        print("\nErros de console JS:", errors)
        assert len(errors) == 0, f"Erros encontrados no console: {errors}"
        print("✅ Todos os 5 testes de interatividade, filtro de data e histórico passaram com 100% de sucesso!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
