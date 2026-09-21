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
        f.write("🎨 MHD TV API Sniffer Dashboard 🎨\n")
        f.write("=" * 45 + "\n\n")

    url = "https://live.mhdtv.online/"
    matches_data = []

    write_status("🔵", "Starting API Sniffer script...")

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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # ব্যাকগ্রাউন্ডের সব নেটওয়ার্ক রিকোয়েস্ট এবং এপিআই কল ট্র্যাক করার লিস্ট
            all_requests = []
            api_responses = []

            def handle_request(request):
                all_requests.append(request.url)

            def handle_response(response):
                # যদি রিকোয়েস্টটি JSON বা এপিআই সম্পর্কিত হয়
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        api_responses.append((response.url, response.text()))
                except:
                    pass

            page.on("request", handle_request)
            page.on("response", handle_response)

            write_status("🟡", f"Navigating to {url}...")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            write_status("🟡", "Waiting 8 seconds to capture background API calls...")
            page.wait_for_timeout(8000)
            
            page_content = page.content()
            write_status("🟢", f"Page processed. Total network requests captured: {len(all_requests)}")

            # যদি প্রক্সি ব্লক খেয়ে থাকে তবুও ক্যাশ বা অন্য কোনো ব্যাকএন্ড এপিআই ধরা পড়েছে কি না দেখা
            if "Anonymous Proxy detected" in page_content:
                write_status("🔴", "Frontend blocked, let's inspect captured API/JSON endpoints:")
            else:
                write_status("🟢", "Frontend loaded successfully!")

            # স্ট্যাটাস ফাইলে সমস্ত ক্যাচ করা এপিআই বা লিংকগুলো লিখে দেওয়া
            with open("status.txt", "a", encoding="utf-8") as f:
                f.write("\n--- CAPTURED API ENDPOINTS & JSON RESPONSES ---\n")
                if api_responses:
                    for req_url, res_text in api_responses[:10]:
                        f.write(f"API URL: {req_url}\n")
                        f.write(f"Response: {res_text[:300]}...\n\n")
                else:
                    f.write("No direct JSON APIs found. Listing all requested URLs:\n")
                    for req in all_requests[:25]:
                        f.write(f"{req}\n")
                f.write("-----------------------------------------------\n")

            browser.close()
            write_status("🔵", "Browser closed.")

        except Exception as e:
            write_status("🔴", f"CRITICAL ERROR: {str(e)}")

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    
    write_status("🟢", f"Execution finished!")

if __name__ == "__main__":
    scrape_mhd_tv()
