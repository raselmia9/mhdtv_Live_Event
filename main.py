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
        f.write("🎨 MHD TV Deep Parser Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", "Starting deep parser script...")

    with sync_playwright() as p:
        try:
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
            
            write_status("🟡", "Waiting 8 seconds for dynamic JavaScript execution...")
            page.wait_for_timeout(8000)
            
            # পেজের সমস্ত টেক্সট বা ইমেলের পাশাপাশি স্ক্রিপ্ট ডেটা বের করা
            content_text = page.inner_text("body")
            write_status("🟢", f"Extracted body text length: {len(content_text)} characters.")

            # যদি ইমজেগুলোর লিংক থেকে ডেটা তোলার সুযোগ থাকে
            images = page.locator("img").all()
            write_status("🔵", f"Total images found on page: {len(images)}")

            # পেজের ভেতর থেকে ম্যাচ কার্ড বা ইভেন্টের ডিটেইলস খুঁজে বের করার চেষ্টা
            # যেহেতু আগের লগে ইভেন্টের ছবি দেখা গেছে, আমরা কার্ডের জেব্রা প্যাটার্ন খুঁজব
            cards = page.locator("div.grid > div, div[class*='rounded'], div[class*='card']").all()
            write_status("🔵", f"Potential card elements found: {len(cards)}")

            for index, card in enumerate(cards):
                try:
                    text = card.inner_text()
                    # যদি টেক্সটে টিম বা খেলার নাম থাকে
                    if len(text) > 10 and ("vs" in text.lower() or "cricket" in text.lower() or "upcoming" in text.lower()):
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        
                        event_title = lines[0] if len(lines) > 0 else "CRICKET MATCH"
                        team1 = lines[1] if len(lines) > 1 else "Team 1"
                        team2 = lines[3] if len(lines) > 3 else "Team 2"
                        match_time = lines[2] if len(lines) > 2 else ""

                        # লোগো সংগ্রহ
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
