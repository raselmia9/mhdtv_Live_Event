import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def write_status(color_dot, message):
    """কালারফুল ডটসহ স্ট্যাটাস বা লগ লেখার ফাংশন"""
    log_line = f"{color_dot} {message}"
    print(log_line)
    with open("status.txt", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def scrape_mhd_tv():
    # স্ক্রিপ্ট শুরু হওয়ার সময় status.txt ফাইলটি ফ্রেশ করে নেওয়া
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write("🎨 MHD TV Scraper Colorful Status Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", f"Starting automation script... Target URL: {url}")

    with sync_playwright() as p:
        try:
            write_status("🟡", "Launching Chromium browser in headless mode...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            write_status("🟡", f"Navigating to {url}...")
            page.goto(url, timeout=60000)
            
            write_status("🟡", "Waiting 6 seconds for page and JavaScript contents to render...")
            page.wait_for_timeout(6000)
            
            page_content = page.content()
            write_status("🟢", f"Page loaded successfully! HTML content length: {len(page_content)} characters.")

            # সম্ভাব্য ম্যাচ কার্ডগুলো খোঁজা
            match_cards = page.locator("div.match-card, div.card, div[class*='match']").all()
            write_status("🔵", f"Total potential match cards detected: {len(match_cards)}")

            if len(match_cards) == 0:
                write_status("🔴", "WARNING: No match cards found! Selectors might need adjustment or site structure changed.")
                write_status("⚪", f"Page body snippet: {page.inner_text('body')[:250]}...")

            for index, card in enumerate(match_cards):
                try:
                    write_status("⚪", f"--- Processing Card Item #{index + 1} ---")
                    
                    # ইভেন্টের নাম
                    try:
                        event_title = card.locator("div[class*='event'], div[class*='league'], span[class*='title']").first.inner_text().strip()
                    except:
                        event_title = "CRICKET MATCH"

                    # ম্যাচের সময়
                    try:
                        match_time = card.locator("div[class*='time'], span[class*='date']").first.inner_text().strip()
                    except:
                        match_time = ""

                    # টিম ১
                    try:
                        team1_title = card.locator("div[class*='team1'] span, div[class*='home'] span").first.inner_text().strip()
                    except:
                        team1_title = "Team 1"

                    try:
                        team1_logo = card.locator("div[class*='team1'] img, div[class*='home'] img").first.get_attribute("src")
                    except:
                        team1_logo = ""

                    # টিম ২
                    try:
                        team2_title = card.locator("div[class*='team2'] span, div[class*='away'] span").first.inner_text().strip()
                    except:
                        team2_title = "Team 2"

                    try:
                        team2_logo = card.locator("div[class*='team2'] img, div[class*='away'] img").first.get_attribute("src")
                    except:
                        team2_logo = ""

                    # স্ট্রিমিং লিঙ্ক
                    streams = []
                    try:
                        stream_elements = card.locator("a[class*='stream'], button[class*='stream'], a[href*='m3u8']").all()
                        for stream in stream_elements:
                            ch_name = stream.inner_text().strip()
                            ch_url = stream.get_attribute("href") or ""
                            if ch_url:
                                if not ch_name:
                                    ch_name = "Stream"
                                streams.append(f"{ch_name},,{ch_url}")
                    except:
                        pass

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

    # JSON ফাইলে ডেটা সেভ করা
    output_file = "matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished! Total matches successfully saved to {output_file}: {len(matches_data)}")

if __name__ == "__main__":
    scrape_mhd_tv()
