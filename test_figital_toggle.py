import os
import sys
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = f"file:///{os.path.join(BASE_DIR, 'index.html').replace(os.sep, '/')}"

def test_toggle():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(HTML_PATH)
        page.wait_for_timeout(1000)

        # Clear localStorage to test clean default state
        page.evaluate("localStorage.clear()")
        page.reload()
        page.wait_for_timeout(1000)

        # 1. State OFF
        badge_text = page.locator("#figitalStateBadge").inner_text()
        ecom_val = page.locator("#ecomMainVal").inner_text()
        dig_val = page.locator("#digMainVal").inner_text()
        ecom_badge_visible = page.locator("#ecomFigitalBadge").is_visible()
        dig_badge_visible = page.locator("#digFigitalBadge").is_visible()

        print(f"[STATE OFF] Badge: {badge_text} | Ecom: {ecom_val} | Dig: {dig_val} | Badges visible: {ecom_badge_visible}/{dig_badge_visible}")
        assert badge_text == "OFF", f"Expected OFF, got {badge_text}"
        assert "30.436" in ecom_val, f"Expected 30.436 in {ecom_val}"
        assert "29.766" in dig_val, f"Expected 29.766 in {dig_val}"
        assert not ecom_badge_visible, "Ecom badge should be hidden"
        assert not dig_badge_visible, "Dig badge should be hidden"

        # Capture screenshot of Top Hero Cards OFF
        page.locator(".top-hero-grid").screenshot(path=os.path.join(BASE_DIR, "preview_hero_cards_off.png"))

        # 2. Click Switch Bar to toggle ON
        print("Clicking Figital switch bar...")
        page.click("#figitalSwitchBar")
        page.wait_for_timeout(500)

        badge_text_on = page.locator("#figitalStateBadge").inner_text()
        ecom_val_on = page.locator("#ecomMainVal").inner_text()
        dig_val_on = page.locator("#digMainVal").inner_text()
        ecom_share_on = page.locator("#ecomPartBadge").inner_text()
        dig_share_on = page.locator("#digPartBadge").inner_text()
        ecom_badge_visible_on = page.locator("#ecomFigitalBadge").is_visible()
        dig_badge_visible_on = page.locator("#digFigitalBadge").is_visible()

        print(f"[STATE ON] Badge: {badge_text_on} | Ecom: {ecom_val_on} | Dig: {dig_val_on} | Share Ecom: {ecom_share_on} | Badges visible: {ecom_badge_visible_on}/{dig_badge_visible_on}")
        assert badge_text_on == "ON", f"Expected ON, got {badge_text_on}"
        assert "31.701" in ecom_val_on, f"Expected 31.701 in {ecom_val_on}"
        assert "31.031" in dig_val_on, f"Expected 31.031 in {dig_val_on}"
        assert ecom_badge_visible_on, "Ecom badge should be visible"
        assert dig_badge_visible_on, "Dig badge should be visible"

        # Capture screenshot of Top Hero Cards ON
        page.locator(".top-hero-grid").screenshot(path=os.path.join(BASE_DIR, "preview_hero_cards_on.png"))

        # 3. Check Visão 4 Projections
        page.click("button[data-view='view-projecoes']")
        page.wait_for_timeout(500)
        proj_ecom_real = page.locator("#proj-real-ecommerce_total").inner_text()
        proj_dig_real = page.locator("#proj-real-canais_digitais").inner_text()
        print(f"[VISAO 4 ON] Proj Ecom: {proj_ecom_real} | Proj Dig: {proj_dig_real}")
        assert "31.701" in proj_ecom_real, f"Expected 31.701 in {proj_ecom_real}"
        assert "31.031" in proj_dig_real, f"Expected 31.031 in {proj_dig_real}"
        page.locator("#view-projecoes .projection-grid").screenshot(path=os.path.join(BASE_DIR, "preview_projecoes_on.png"))

        # 4. Toggle back OFF
        page.click("button[data-view='view-geral']")
        page.wait_for_timeout(300)
        page.click("#figitalSwitchBar")
        page.wait_for_timeout(500)

        badge_text_off2 = page.locator("#figitalStateBadge").inner_text()
        ecom_val_off2 = page.locator("#ecomMainVal").inner_text()
        dig_val_off2 = page.locator("#digMainVal").inner_text()
        print(f"[STATE BACK OFF] Badge: {badge_text_off2} | Ecom: {ecom_val_off2} | Dig: {dig_val_off2}")
        assert badge_text_off2 == "OFF"
        assert "30.436" in ecom_val_off2
        assert "29.766" in dig_val_off2

        # 5. Full page screenshot
        page.screenshot(path=os.path.join(BASE_DIR, "preview_full_page_off.png"), full_page=True)

        browser.close()
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    test_toggle()
