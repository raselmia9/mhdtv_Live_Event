import json
import os
from playwright.sync_api import sync_playwright

def write_status(color_dot, message):
    log_line = f"{color_dot} {message}"
    print(log_line)
    with open("status.txt", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def scrape_mhd_tv():
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write("🎨 MHD TV Scraper Colorful Status Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", "Starting streamlined scraper...")

    with sync_playwright() as p:
        try:
            write_status("🟡", "Launching Chromium browser...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--window-size=1920,1080",
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            write_status("🟡", f"Navigating to {url}...")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            write_status("🟡", "Waiting 6 seconds for page content...")
            page.wait_for_timeout(6000)
            
            page_content = page.content()
            write_status("🟢", f"Page loaded! HTML content length: {len(page_content)} characters.")

            if "Anonymous Proxy detected" in page_content:
                write_status("🔴", "BLOCK DETECTED: Target server blocked the runner IP.")
            else:
                write_status("🟢", "SUCCESS: Page accessed!")
                
                # কার্ড বা ডেটা খোঁজা
                match_cards = page.locator("div.match-card, div.card, div[class*='match'], div.grid > div").all()
                write_status("🔵", f"Total potential cards found: {len(match_cards)}")

                for index, card in enumerate(match_cards):
                    try:
                        card_text = card.inner_text()
                        if "vs" not in card_text.lower():
                            continue

                        event_title = card.locator("div[class*='event'], div[class*='league'], span").first.inner_text().strip()
                        match_time = card.locator("div[class*='time'], span[class*='date']").first.inner_text().strip() if card.locator("div[class*='time'], span[class*='date']").count() > 0 else ""
                        
                        images = card.locator("img").all()
                        team1_logo = images[0].get_attribute("src") if len(images) > 0 else ""
                        team2_logo = images[1].get_attribute("src") if len(images) > 1 else ""

                        lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                        team1_title = lines[1] if len(lines) > 1 else "Team 1"
                        team2_title = lines[3] if len(lines) > 3 else "Team 2"

                        match_item = {
                            "eventTitle": event_title if event_title else "CRICKET MATCH",
                            "matchTime": match_time,
                            "team1Logo": team1_logo,
                            "team2Logo": team2_logo,
                            "team1Title": team1_title,
                            "team2Title": team2_title,
                            "streamLink": "",
                            "isHot": True
                        }
                        matches_data.append(match_item)
                        write_status("🟢", f"Extracted: {team1_title} vs {team2_title}")
                    except:
                        pass

            browser.close()
            write_status("🔵", "Browser closed.")

        except Exception as e:
            write_status("🔴", f"CRITICAL ERROR: {str(e)}")

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished! Saved matches: {len(matches_data)}")

if __name__ == "__main__":
    scrape_mhd_tv()
