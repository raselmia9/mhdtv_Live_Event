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
        f.write("🎨 MHD TV Stealth Parser Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", "Starting advanced stealth scraper...")

    with sync_playwright() as p:
        try:
            # আরও নিখুঁত অ্যান্টি-বট আর্গুমেন্ট
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
                locale="en-US",
                timezone_id="Asia/Dhaka"
            )
            
            # রোবট ডিটেকশন এড়ানোর জন্য জাভাস্ক্রিপ্ট প্রপার্টি ওভাররাইড
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                window.chrome = { runtime: {} };
            """)
            
            page = context.new_page()

            write_status("🟡", f"Navigating to {url} with stealth mode...")
            page.goto(url, timeout=60000, wait_until="networkidle")
            
            write_status("🟡", "Simulating human interaction (Scrolling & Waiting)...")
            page.mouse.move(200, 200)
            page.mouse.down()
            page.mouse.up()
            
            # পেজ পুরোপুরি রেন্ডার হওয়ার জন্য ১০ সেকেন্ড সময় দেওয়া
            page.wait_for_timeout(10000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)
            
            content_text = page.inner_text("body")
            write_status("🟢", f"Extracted body text length: {len(content_text)} characters.")

            # যদি কন্টেন্ট ঠিকমতো লোড হয়ে থাকে
            cards = page.locator("div.grid > div, div[class*='rounded'], div[class*='card'], article").all()
            write_status("🔵", f"Potential card elements found: {len(cards)}")

            for index, card in enumerate(cards):
                try:
                    text = card.inner_text()
                    if len(text) > 10 and "vs" in text.lower():
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        
                        event_title = lines[0] if len(lines) > 0 else "CRICKET MATCH"
                        team1 = lines[1] if len(lines) > 1 else "Team 1"
                        team2 = lines[3] if len(lines) > 3 else "Team 2"
                        match_time = lines[2] if len(lines) > 2 else ""

                        card_images = card.locator("img").all()
                        t1_logo = card_images[0].get_attribute("src") if len(card_images) > 0 else ""
                        t2_logo = card_images[1].get_attribute("src") if len(card_images) > 1 else ""

                        match_item = {
                            "eventTitle": event_title,
                            "matchTime": match_time,
                            "team1Logo": t1_logo,
                            "team2Logo": t2_logo,
                            "team1Title": team1,
                            "team2Title": team2,
                            "streamLink": "",
                            "isHot": True
                        }
                        matches_data.append(match_item)
                        write_status("🟢", f"Successfully parsed match: {team1} vs {team2}")
                except:
                    pass

            browser.close()
            write_status("🔵", "Browser closed.")

        except Exception as e:
            write_status("🔴", f"CRITICAL ERROR: {str(e)}")

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished! Total matches saved: {len(matches_data)}")

if __name__ == "__main__":
    scrape_mhd_tv()
