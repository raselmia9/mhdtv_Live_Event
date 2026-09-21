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

    write_status("🔵", f"Starting deep-diagnostic script... Target URL: {url}")

    with sync_playwright() as p:
        try:
            write_status("🟡", "Launching browser with enhanced headers and fake geo-location...")
            
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--window-size=1920,1080",
                    "--disable-dev-shm-usage"
                ]
            )
            
            # রিয়েল মোবাইল বা ডেস্কটপ ব্রাউজার হেডার পাস করা যাতে প্রক্সি ব্লক বাইপাস করা যায়
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Referer": "https://google.com"
                }
            )
            
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # নেটওয়ার্ক রিকোয়েস্ট ট্র্যাক করার জন্য (যদি ওয়েবসাইট কোনো এপিআই কল করে)
            api_requests = []
            page.on("request", lambda request: api_requests.append(request.url))

            write_status("🟡", f"Navigating to {url}...")
            response = page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            if response:
                write_status("🔵", f"HTTP Response Status Code: {response.status}")
            
            write_status("🟡", "Waiting 8 seconds for full JS rendering and API calls...")
            page.wait_for_timeout(8000)
            
            page_content = page.content()
            write_status("🟢", f"Page loaded! HTML content length: {len(page_content)} characters.")

            # যদি প্রক্সি ব্লক মেসেজ ধরা পড়ে
            if "Anonymous Proxy detected" in page_content:
                write_status("🔴", "BLOCK DETECTED: The host server's firewall/proxy filter is rejecting GitHub datacenter IPs.")
                write_status("⚪", "Let's check captured network requests to find direct backend API:")
                for req in api_requests[:10]:
                    write_status("🔵", f"Captured URL: {req}")
            else:
                write_status("🟢", "SUCCESS: Block bypassed successfully!")

            # ওয়েবসাইটের ম্যাচ কার্ডগুলো খোঁজা
            match_cards = page.locator("div.match-card, div.card, div[class*='match']").all()
            write_status("🔵", f"Total potential match cards detected: {len(match_cards)}")

            for index, card in enumerate(match_cards):
                try:
                    write_status("⚪", f"--- Processing Card Item #{index + 1} ---")
                    
                    event_title = card.locator("div[class*='event'], div[class*='league'], span[class*='title']").first.inner_text().strip() if card.locator("div[class*='event'], div[class*='league'], span[class*='title']").count() > 0 else "CRICKET MATCH"
                    match_time = card.locator("div[class*='time'], span[class*='date']").first.inner_text().strip() if card.locator("div[class*='time'], span[class*='date']").count() > 0 else ""
                    
                    team1_title = card.locator("div[class*='team1'] span, div[class*='home'] span").first.inner_text().strip() if card.locator("div[class*='team1'] span, div[class*='home'] span").count() > 0 else "Team 1"
                    team1_logo = card.locator("div[class*='team1'] img, div[class*='home'] img").first.get_attribute("src") if card.locator("div[class*='team1'] img, div[class*='home'] img").count() > 0 else ""
                    
                    team2_title = card.locator("div[class*='team2'] span, div[class*='away'] span").first.inner_text().strip() if card.locator("div[class*='team2'] span, div[class*='away'] span").count() > 0 else "Team 2"
                    team2_logo = card.locator("div[class*='team2'] img, div[class*='away'] img").first.get_attribute("src") if card.locator("div[class*='team2'] img, div[class*='away'] img").count() > 0 else ""

                    streams = []
                    stream_elements = card.locator("a[class*='stream'], button[class*='stream'], a[href*='m3u8']").all()
                    for stream in stream_elements:
                        ch_name = stream.inner_text().strip()
                        ch_url = stream.get_attribute("href") or ""
                        if ch_url:
                            if not ch_name:
                                ch_name = "Stream"
                            streams.append(f"{ch_name},,{ch_url}")

                    stream_link_str = ",) ".join(streams) if streams else ""

                    match_item = {
                        "eventTitle": event_title,
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
                    write_status("🔴", f"Error parsing card #{index + 1}: {str(card_err)}")

            browser.close()
            write_status("🔵", "Browser closed gracefully.")

        except Exception as e:
            write_status("🔴", f"CRITICAL ERROR during Playwright execution: {str(e)}")

    output_file = "matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished! Total matches successfully saved to {output_file}: {len(matches_data)}")

if __name__ == "__main__":
    scrape_mhd_tv()
