import json
import os
import requests
from playwright.sync_api import sync_playwright

def write_status(color_dot, message):
    log_line = f"{color_dot} {message}"
    print(log_line)
    with open("status.txt", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def get_free_proxy():
    """ফ্রী প্রক্সি পাওয়ার জন্য একটি পাবলিক প্রক্সি এপিআই ব্যবহার করা"""
    try:
        response = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite", timeout=5)
        if response.status_code == 200:
            proxies = response.text.splitlines()
            if proxies:
                return f"http://{proxies[0]}"
    except:
        pass
    return None

def scrape_mhd_tv():
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write("🎨 MHD TV Scraper Colorful Status Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", "Starting proxy-enabled stealth scraper...")

    with sync_playwright() as p:
        try:
            # একটি ফ্রী প্রক্সি সংগ্রহ করার চেষ্টা
            proxy_server = get_free_proxy()
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--window-size=1920,1080",
            ]
            
            browser_options = {"headless": True, "args": launch_args}
            if proxy_server:
                write_status("🟢", f"Using Proxy to bypass IP block: {proxy_server}")
                browser_options["proxy"] = {"server": proxy_server}
            else:
                write_status("🟡", "No proxy found, running with standard stealth headers...")

            browser = p.chromium.launch(**browser_options)
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive"
                }
            )
            
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            write_status("🟡", f"Navigating to {url}...")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            write_status("🟡", "Waiting 8 seconds for JS rendering...")
            page.wait_for_timeout(8000)
            
            page_content = page.content()
            write_status("🟢", f"Page loaded! HTML content length: {len(page_content)} characters.")

            if "Anonymous Proxy detected" in page_content:
                write_status("🔴", "BLOCKED: Proxy or Datacenter IP detected again.")
            else:
                write_status("SUCCESS", "Anti-bot proxy block successfully bypassed!")
                
                # কার্ডগুলো সংগ্রহ করা
                match_cards = page.locator("div.match-card, div.card, div[class*='match'], div.grid > div").all()
                write_status("🔵", f"Total potential match cards detected: {len(match_cards)}")

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
