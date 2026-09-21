import json
import os
import requests
from bs4 import BeautifulSoup

def scrape_mhd_tv():
    url = "https://live.mhdtv.online/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    matches_data = []
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ওয়েবসাইটের স্ট্রাকচার অনুযায়ী এখানে কার্ড পার্সিং লজিক বসাতে হবে।
            # যেহেতু আপনি আপনার কাঙ্ক্ষিত JSON ফরম্যাট আগে থেকেই ডিফাইন করে দিয়েছেন,
            # ওয়েবসাইট থেকে ডেটা এক্সট্রাক্ট করে এই matches_data লিস্টে ডিকশনারি আকারে যুক্ত করতে হবে।
            
        else:
            print(f"Failed to fetch website. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error occurred: {e}")

    # আউটপুট JSON ফাইলে সেভ করা
    output_file = "matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scrape_mhd_tv()
