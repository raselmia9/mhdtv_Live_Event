import json
import os
from playwright.sync_api import sync_playwright

def write_status(color_dot, message):
    log_line = f"{color_dot} {message}"
    print(log_line)
    with open("status.txt", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def scrape_mhd_tv():
    # প্রথমে status.txt ফাইলটি ফ্রেশ করে হেডার লেখা
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write("🎨 MHD TV Scraper Colorful Status Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", f"Starting full-body dump script... Target URL: {url}")

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

            # যদি পেজ সাইজ খুব ছোট বা ব্লকিং মেসেজ থাকে
            if len(page_content) < 500:
                write_status("🔴", f"WARNING: Page content is too short! Raw content: {page_content}")
            else:
                write_status("🟢", "SUCCESS: Full page content captured. Dumping body snippet below:")
                
                # সম্পূর্ণ বডি বা এইচটিএমএল কোডের মূল অংশটি status.txt ফাইলে যুক্ত করা 
                # (যাতে আপনি কপি করে দিতে পারেন)
                body_html = page.inner_html("body")
                
                with open("status.txt", "a", encoding="utf-8") as f:
                    f.write("\n--- START OF RAW HTML BODY ---\n")
                    f.write(body_html[:5000])  # প্রথম ৫০০০ ক্যারেক্টার স্ট্যাটাসে ডাম্প হবে
                    f.write("\n--- END OF RAW HTML BODY ---\n")

            browser.close()
            write_status("🔵", "Browser closed gracefully.")

        except Exception as e:
            write_status("🔴", f"CRITICAL ERROR during Playwright execution: {str(e)}")

    output_file = "matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished!")

if __name__ == "__main__":
    scrape_mhd_tv()
