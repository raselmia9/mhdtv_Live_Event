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

    write_status("🔵", f"Starting scraper... Target URL: {url}")

    with sync_playwright() as p:
        try:
            write_status("🟡", "Launching browser...")
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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            write_status("🟡", f"Navigating to {url}...")
            page.goto(url, timeout=60000, wait_until="networkidle")
            
            write_status("🟡", "Waiting 8 seconds for full JavaScript and match cards to render...")
            page.wait_for_timeout(8000)
            
            page_content = page.content()
            write_status("🟢", f"Page loaded! HTML content length: {len(page_content)} characters.")

            # যেহেতু আগের সিলেক্টর কাজ করেনি, এবার আমরা আরও বিস্তৃত সিলেক্টর ব্যবহার করছি 
            # (যেমন: গ্রিড আইটেম, লিভ বা আপকামিং সেকশনের কার্ডগুলো ধরতে পারে এমন ট্যাগ)
            match_cards = page.locator("div.grid > div, div[class*='rounded'], div[class*='bg-'], main div div").all()
            write_status("🔵", f"Total potential match cards detected with new selector: {len(match_cards)}")

            # যদি সরাসরি কার্ড না পাওয়া যায়, তবে পেজের ভেতরের সব ইমেজ বা লিংক ট্র্যাক করে ডেটা তোলার চেষ্টা করা হবে
            valid_cards_found = 0

            for index, card in enumerate(match_cards):
                try:
                    # ভেତরে টিম বা ইভেন্ট সম্পর্কিত টেক্সট আছে কি না চেক করা
                    card_text = card.inner_text()
                    if "vs" not in card_text.lower() and "CRICKET" not in card_text and "UPCOMING" not in card_text:
                        continue # যেগুলোতে খেলা নেই সেগুলো স্কিপ করবে

                    valid_cards_found += 1
                    write_status("⚪", f"--- Processing Valid Match Card #{valid_cards_found} ---")
                    
                    # ইভেন্টের নাম খোঁজা
                    try:
                        event_title = card.locator("div, span").filter(has_text=re.compile("CRICKET|FOOTBALL|ICC|LANKA|BPL|IPL", re.IGNORECASE)).first.inner_text().strip()
                    except:
                        event_title = "CRICKET MATCH"

                    # ম্যাচের সময়
                    try:
                        match_time = card.locator("span, div").filter(has_text=re.compile(r"\d{4}-\d{2}-\d{2}|AM|PM|Starts", re.IGNORECASE)).first.inner_text().strip()
                    except:
                        match_time = ""

                    # টিমগুলোর নাম ও লোগো সংগ্রহ
                    images = card.locator("img").all()
                    team1_logo = images[0].get_attribute("src") if len(images) > 0 else ""
                    team2_logo = images[1].get_attribute("src") if len(images) > 1 else ""

                    # টেক্সট থেকে টিম নাম বের করা
                    lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                    team1_title = lines[1] if len(lines) > 1 else "Team 1"
                    team2_title = lines[3] if len(lines) > 3 else "Team 2"

                    # স্ট্রিমিং লিঙ্ক
                    streams = []
                    links = card.locator("a").all()
                    for link in links:
                        l_text = link.inner_text().strip()
                        l_href = link.get_attribute("href") or ""
                        if l_href and ("m3u8" in l_href or "http" in l_href):
                            streams.append(f"{l_text if l_text else 'Stream'},,{l_href}")

                    stream_link_str = ",) ".join(streams) if streams else ""

                    match_item = {
                        "eventTitle": event_title if event_title else "CRICKET MATCH",
                        "matchTime": match_time,
                        "team1Logo": team1_logo,
                        "team2Logo": team2_logo,
                        "team1Title": team1_title,
                        "team2Title": team2_title,
                        "streamLink": stream_link_str,
                        "isHot": True
                    }
                    
                    matches_data.append(match_item)
                    write_status("🟢", f"Successfully extracted: {team1_title} vs {team2_title}")

                except Exception as card_err:
                    pass # অপ্রয়োজনীয় এরর এড়াতে সাইলেন্ট রাখা হলো

            browser.close()
            write_status("🔵", "Browser closed gracefully.")

        except Exception as e:
            write_status("🔴", f"CRITICAL ERROR during Playwright execution: {str(e)}")

    output_file = "matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished! Total matches successfully saved to {output_file}: {len(matches_data)}")

if __name__ == "__main__":
    import re
    scrape_mhd_tv()
