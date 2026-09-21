import json
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
            
            # ওয়েবসাইটের কার্ড স্ট্রাকচার অনুযায়ী প্রতিটি ম্যাচের কার্ড সিলেক্ট করা
            # (নোট: ওয়েবসাইটের আসল HTML ক্লাস নেম বা ট্যাগ অনুযায়ী নিচে সিলেক্টর অ্যাডজাস্ট করা হতে পারে)
            match_cards = soup.find_all('div', class_='match-card') # উদাহরণের জন্য ক্লাস নেম দেওয়া হয়েছে
            
            for card in match_cards:
                try:
                    # ইভেন্টের নাম বা লিগ টাইটেল
                    event_title = card.find('div', class_='event-title').get_text(strip=True) if card.find('div', class_='event-title') else "CRICKET MATCH"
                    
                    # খেলার সময়
                    match_time = card.find('div', class_='match-time').get_text(strip=True) if card.find('div', class_='match-time') else ""
                    
                    # টিম ১ এর তথ্য
                    team1_elem = card.find('div', class_='team-1')
                    team1_title = team1_elem.find('span', class_='team-name').get_text(strip=True) if team1_elem and team1_elem.find('span', class_='team-name') else "Team 1"
                    team1_logo = team1_elem.find('img')['src'] if team1_elem and team1_elem.find('img') else ""
                    
                    # টিম ২ এর তথ্য
                    team2_elem = card.find('div', class_='team-2')
                    team2_title = team2_elem.find('span', class_='team-name').get_text(strip=True) if team2_elem and team2_elem.find('span', class_='team-name') else "Team 2"
                    team2_logo = team2_elem.find('img')['src'] if team2_elem and team2_elem.find('img') else ""
                    
                    # স্ট্রিমিং লিঙ্কগুলো সংগ্রহ করে আপনার কাঙ্ক্ষিত ফরম্যাটে সাজানো: ChannelName,,StreamLink,)
                    streams = []
                    stream_elements = card.find_all('a', class_='stream-link') # স্ট্রিম লিংকের ট্যাগ
                    for stream in stream_elements:
                        channel_name = stream.get_text(strip=True)
                        stream_url = stream.get('href', '')
                        if channel_name and stream_url:
                            streams.append(f"{channel_name},,{stream_url}")
                    
                    # যদি একাধিক লিংক থাকে তবে আপনার ফরম্যাট অনুযায়ী জোড়া লাগানো
                    stream_link_str = ",) ".join(streams) if streams else ""
                    
                    # ডিকশনারি আকারে লিস্টে যুক্ত করা
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
                    
                except Exception as inner_e:
                    print(f"Error parsing individual match card: {inner_e}")
                    
        else:
            print(f"Failed to fetch website. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error occurred during request: {e}")

    # ডেটা না পেলে বা ডিবাগিংয়ের জন্য ফলব্যাক স্যাম্পল ডাটা রাখতে পারেন, অথবা ফাঁকা লিস্ট সেव হবে
    output_file = "matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=4, ensure_ascii=False)
    print(f"Successfully saved {len(matches_data)} matches to {output_file}")

if __name__ == "__main__":
    scrape_mhd_tv()
